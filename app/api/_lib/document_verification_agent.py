# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Document Verification Agent using Strands Agents"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional
import asyncio
from strands_agents import Agent, Tool
from strands_agents.memory import SimpleMemory
from .models import AgentRequest, VerificationStatus

class DocumentVerificationAgent:
    """Document Verification Agent using Strands Agents"""

    def __init__(self, services, logger):
        self.db_service = services['db_service']
        self.s3_service = services['s3_service']
        self.bedrock_client = services['bedrock_client']
        self.logger = logger

        # Initialize Strands Agent
        self.agent = self._initialize_agent()

    def _initialize_agent(self) -> Agent:
        """Initialize the Strands Agent with tools and memory"""
        # Create memory for the agent
        memory = SimpleMemory()

        # Define tools for the agent
        tools = [
            Tool(
                name="analyze_document_image",
                description="Analyzes a document image and extracts information",
                function=self._analyze_document_image
            ),
            Tool(
                name="verify_document_authenticity",
                description="Verifies if a document appears authentic based on various checks",
                function=self._verify_document_authenticity
            ),
            Tool(
                name="extract_document_fields",
                description="Extracts specific fields from a document based on document type",
                function=self._extract_document_fields
            ),
            Tool(
                name="check_document_consistency",
                description="Checks if all fields in the document are consistent with each other",
                function=self._check_document_consistency
            )
        ]

        # Create the agent
        agent = Agent(
            name="DocumentVerificationAgent",
            description="An agent that verifies documents for authenticity and extracts information",
            tools=tools,
            memory=memory,
            model_id="amazon.nova-lite-v1:0",  # Use the active model from config in production
            bedrock_client=self.bedrock_client
        )

        return agent

    async def start_verification(self, request: AgentRequest) -> Dict:
        """Start a new document verification process"""
        try:
            # Generate a unique ID for this verification
            verification_id = str(uuid.uuid4())

            # Upload image to S3
            file_key = self.s3_service.upload_base64_image(request.image_base64)
            self.logger.info(f"Image uploaded with key: {file_key}")

            # Create initial verification record
            current_time = datetime.now(timezone.utc).isoformat()
            verification = {
                'verification_id': verification_id,
                'status': VerificationStatus.IN_PROGRESS,
                'document_type': request.document_type,
                'steps': [],
                'file_key': file_key,
                'created_at': current_time,
                'updated_at': current_time
            }

            # Save to database
            await self.db_service.save_agent_verification(verification)

            # Start the verification process asynchronously
            # In a production environment, you would use Step Functions or another async mechanism
            asyncio.create_task(self._run_verification(verification_id, request.image_base64, request.document_type))

            # Return the verification ID and initial status
            return {
                'verification_id': verification_id,
                'status': VerificationStatus.IN_PROGRESS,
                'message': 'Verification process started'
            }

        except Exception as e:
            self.logger.error(f"Error starting verification: {str(e)}", exc_info=True)
            raise

    async def get_verification_status(self, verification_id: str) -> Optional[Dict]:
        """Get the status of a verification process"""
        try:
            # Get verification from database
            verification = await self.db_service.get_agent_verification(verification_id)

            if not verification:
                return None

            # Add presigned URL for preview if file exists
            if verification.get('file_key'):
                verification['preview_url'] = self.s3_service.get_presigned_url(verification['file_key'])

            return verification

        except Exception as e:
            self.logger.error(f"Error getting verification status: {str(e)}", exc_info=True)
            raise

    async def provide_additional_info(self, verification_id: str, additional_info: Dict) -> Dict:
        """Process additional information for a verification"""
        try:
            # Get current verification
            verification = await self.db_service.get_agent_verification(verification_id)

            if not verification:
                raise ValueError(f"Verification with ID {verification_id} not found")

            if verification['status'] != VerificationStatus.NEEDS_INFO:
                raise ValueError(f"Verification is not in NEEDS_INFO state, current state: {verification['status']}")

            # Update verification with additional info
            verification['additional_info'] = additional_info
            verification['status'] = VerificationStatus.IN_PROGRESS
            verification['updated_at'] = datetime.now(timezone.utc).isoformat()

            # Save updated verification
            await self.db_service.update_agent_verification(verification)

            # Continue verification process asynchronously
            asyncio.create_task(self._continue_verification(verification_id, additional_info))

            return {
                'verification_id': verification_id,
                'status': VerificationStatus.IN_PROGRESS,
                'message': 'Verification process continued with additional information'
            }

        except ValueError as ve:
            raise ve
        except Exception as e:
            self.logger.error(f"Error processing additional info: {str(e)}", exc_info=True)
            raise

    async def _run_verification(self, verification_id: str, image_base64: str, document_type: Optional[str] = None):
        """Run the verification process using Strands Agent"""
        try:
            # Set up the agent with context
            self.agent.memory.add("verification_id", verification_id)
            self.agent.memory.add("document_image", image_base64)
            if document_type:
                self.agent.memory.add("document_type", document_type)

            # Define the task for the agent
            task = """
            You are a document verification expert. Your task is to verify the authenticity of the provided document
            and extract relevant information from it. Follow these steps:

            1. Analyze the document image to determine the document type if not already provided
            2. Verify the document's authenticity by checking for security features and signs of tampering
            3. Extract key fields from the document based on its type
            4. Check the consistency of the extracted information
            5. Provide a final verification result with confidence score

            If you need additional information at any point, specify exactly what you need.
            """

            # Run the agent
            result = await self.agent.run(task)

            # Process the result and update verification status
            await self._process_agent_result(verification_id, result)

        except Exception as e:
            self.logger.error(f"Error running verification: {str(e)}", exc_info=True)
            # Update verification status to failed
            await self._update_verification_status(
                verification_id, VerificationStatus.FAILED, error_message=str(e))

    async def _continue_verification(self, verification_id: str, additional_info: Dict):
        """Continue the verification process with additional information"""
        try:
            # Get current verification
            verification = await self.db_service.get_agent_verification(verification_id)

            # Add additional info to agent memory
            self.agent.memory.add("additional_info", additional_info)

            # Define the continuation task
            task = """
            Continue the document verification process with the additional information provided.
            Review the new information and update your verification results accordingly.
            """

            # Run the agent
            result = await self.agent.run(task)

            # Process the result and update verification status
            await self._process_agent_result(verification_id, result)

        except Exception as e:
            self.logger.error(f"Error continuing verification: {str(e)}", exc_info=True)
            # Update verification status to failed
            await self._update_verification_status(
                verification_id, VerificationStatus.FAILED, error_message=str(e))

    async def _process_agent_result(self, verification_id: str, result: Dict):
        """Process the result from the agent and update verification status"""
        try:
            # Get current verification
            verification = await self.db_service.get_agent_verification(verification_id)

            # Extract information from result
            needs_info = result.get('needs_additional_info')

            if needs_info:
                # Agent needs more information
                verification['status'] = VerificationStatus.NEEDS_INFO
                verification['needs_info'] = needs_info
            else:
                # Agent completed verification
                verification['status'] = VerificationStatus.COMPLETED
                verification['confidence'] = result.get('confidence', 0.0)
                verification['result_summary'] = result.get('summary', '')
                verification['document_type'] = result.get('document_type', verification.get('document_type'))

            # Add any new steps
            if 'steps' in result:
                for step in result['steps']:
                    step_record = {
                        'step_id': str(uuid.uuid4()),
                        'name': step['name'],
                        'description': step['description'],
                        'status': step['status'],
                        'confidence': step.get('confidence'),
                        'details': step.get('details'),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                    verification['steps'].append(step_record)

            verification['updated_at'] = datetime.now(timezone.utc).isoformat()

            # Save updated verification
            await self.db_service.update_agent_verification(verification)

        except Exception as e:
            self.logger.error(f"Error processing agent result: {str(e)}", exc_info=True)
            # Update verification status to failed
            await self._update_verification_status(
                verification_id, VerificationStatus.FAILED, error_message=str(e))

    async def _update_verification_status(self, verification_id: str, status: VerificationStatus, 
                                        error_message: Optional[str] = None):
        """Update the status of a verification"""
        try:
            # Get current verification
            verification = await self.db_service.get_agent_verification(verification_id)

            if not verification:
                self.logger.error(f"Verification with ID {verification_id} not found")
                return

            # Update status
            verification['status'] = status
            verification['updated_at'] = datetime.now(timezone.utc).isoformat()

            if error_message:
                verification['error'] = error_message

            # Save updated verification
            await self.db_service.update_agent_verification(verification)

        except Exception as e:
            self.logger.error(f"Error updating verification status: {str(e)}", exc_info=True)

    # Tool implementations
    async def _analyze_document_image(self, image_base64: str) -> Dict:
        """Analyze a document image to determine its type and basic properties"""
        # In a real implementation, this would use Bedrock or another service
        # For now, we'll return mock data
        return {
            "document_type": "passport",
            "image_quality": "high",
            "confidence": 0.92,
            "details": {
                "dimensions": "3.5x4.5 inches",
                "resolution": "300 DPI",
                "format": "color"
            }
        }

    async def _verify_document_authenticity(self, image_base64: str, document_type: str) -> Dict:
        """Verify if a document appears authentic"""
        # In a real implementation, this would check security features
        return {
            "is_authentic": True,
            "confidence": 0.85,
            "security_features_detected": [
                "microprint",
                "hologram",
                "uv_reactive_elements"
            ],
            "potential_issues": []
        }

    async def _extract_document_fields(self, image_base64: str, document_type: str) -> Dict:
        """Extract fields from a document based on its type"""
        # In a real implementation, this would extract actual fields
        return {
            "fields": {
                "name": "John Doe",
                "date_of_birth": "1980-01-01",
                "document_number": "AB123456",
                "expiry_date": "2030-01-01",
                "issuing_country": "United States"
            },
            "confidence": {
                "name": 0.95,
                "date_of_birth": 0.92,
                "document_number": 0.98,
                "expiry_date": 0.94,
                "issuing_country": 0.99
            }
        }

    async def _check_document_consistency(self, fields: Dict) -> Dict:
        """Check if document fields are consistent with each other"""
        # In a real implementation, this would check for inconsistencies
        return {
            "is_consistent": True,
            "confidence": 0.90,
            "inconsistencies": []
        }
