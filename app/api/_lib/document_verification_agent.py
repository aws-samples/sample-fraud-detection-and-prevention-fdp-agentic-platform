# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Document Verification Agent using Strands Agents"""

import uuid
import json
import base64
from datetime import datetime, timezone
from typing import Dict, Optional, Any, List
import asyncio
from strands import Agent, tool
from strands.models import BedrockModel
from .models import AgentRequest, VerificationStatus

class DocumentVerificationAgent:
    """Document Verification Agent using Strands Agents"""

    def __init__(self, services, logger):
        self.db_service = services['db_service']
        self.s3_service = services['s3_service']
        self.bedrock_client = services['bedrock_client']
        self.logger = logger

        # Initialize agent memory
        self.agent_memory = {}

        # Initialize Strands Agent
        self.agent = self._initialize_agent()

        # Nova Lite model ID for LLM tasks
        self.nova_model_id = "amazon.nova-lite-v1:0"

    def _initialize_agent(self) -> Agent:
        """Initialize the Strands Agent with tools and memory"""
        # Create a Bedrock model
        bedrock_model = BedrockModel(
            model_id="amazon.nova-lite-v1:0",
            temperature=0.2,
            streaming=False,
            client=self.bedrock_client
        )

        # Create the agent with the Bedrock model
        agent = Agent(
            tools=[
                self._analyze_document_image,
                self._verify_document_authenticity,
                self._extract_document_fields,
                self._check_document_consistency
            ],
            model=bedrock_model
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
                'pk': verification_id,
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
            # Reset agent memory for this new verification
            self.agent_memory.clear()

            # Set up context for the agent
            context = {
                "verification_id": verification_id,
                "document_image": image_base64
            }
            if document_type:
                context["document_type"] = document_type

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

            # Run the agent with context
            result = await self.agent(task, context=context)

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

            # Create context with additional info and document data
            context = {
                "additional_info": additional_info,
                "verification_id": verification_id
            }

            # Add document image if available
            if "document_image" in self.agent_memory:
                context["document_image"] = self.agent_memory["document_image"]

            # Add document type if available
            if verification.get("document_type"):
                context["document_type"] = verification.get("document_type")

            # Define the continuation task
            task = """
            Continue the document verification process with the additional information provided.
            Review the new information and update your verification results accordingly.
            """

            # Run the agent with context
            result = await self.agent(task, context=context)

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

            # In 0.1.6, the response format is different
            # Extract the agent's response from the result
            agent_response = result.get("response", {})
            tool_executions = result.get("tool_executions", [])

            # Update memory with extracted information
            for execution in tool_executions:
                if execution.get("tool_name") == "extract_document_fields" and "result" in execution:
                    if "fields" in execution["result"]:
                        self.agent_memory["extracted_fields"] = execution["result"]["fields"]

                if execution.get("tool_name") == "analyze_document_image" and "result" in execution:
                    if "document_type" in execution["result"]:
                        self.agent_memory["document_type"] = execution["result"]["document_type"]

            # Check if agent indicated it needs more information
            needs_info = False
            info_request = None

            # Look for mentions of additional info needed in the response
            if "need more information" in agent_response.lower() or "additional information needed" in agent_response.lower():
                needs_info = True
                info_request = agent_response

            if needs_info:
                # Agent needs more information
                verification['status'] = VerificationStatus.NEEDS_INFO
                verification['needs_info'] = info_request
            else:
                # Extract results from tool executions and response
                verification['status'] = VerificationStatus.COMPLETED

                # Try to extract a confidence score
                confidence = 0.0
                for execution in tool_executions:
                    if execution.get("result", {}).get("confidence"):
                        confidence = max(confidence, float(execution["result"]["confidence"]))

                verification['confidence'] = confidence
                verification['result_summary'] = agent_response

                # Try to extract document type if available
                for execution in tool_executions:
                    if "document_type" in execution.get("result", {}):
                        verification['document_type'] = execution["result"]["document_type"]
                        break

                # Add extracted fields if available
                for execution in tool_executions:
                    if execution.get("tool_name") == "extract_document_fields" and "result" in execution:
                        if "fields" in execution["result"]:
                            verification['extracted_fields'] = execution["result"]["fields"]

            # Add tool executions as steps
            for execution in tool_executions:
                step_record = {
                    'step_id': str(uuid.uuid4()),
                    'name': execution.get('tool_name', 'Unknown tool'),
                    'description': execution.get('tool_input', {}),
                    'status': 'completed',
                    'details': execution.get('result', {}),
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

    # Tool implementations using Amazon Nova
    @tool
    async def _analyze_document_image(self, image_base64: str) -> Dict:
        """Analyze a document image to determine its type and basic properties using Nova Lite"""
        try:
            # Get image from memory if not provided directly
            if not image_base64 and "document_image" in self.agent_memory:
                image_base64 = self.agent_memory["document_image"]

            if not image_base64:
                return {
                    "document_type": "unknown",
                    "image_quality": "unknown",
                    "confidence": 0.0,
                    "error": "No image provided"
                }

            # Prepare prompt for Nova Lite multimodal model
            prompt = """
            Analyze this document image and determine:
            1. What type of document it is (e.g., passport, driver's license, ID card, birth certificate, etc.)
            2. The quality of the image (high, medium, low)
            3. Any noticeable features or characteristics of the document

            Format your response as JSON with the following format:
            {
                "document_type": "document type",
                "image_quality": "quality level",
                "confidence": 0.0-1.0,
                "details": {
                    "dimensions": "dimensions if visible",
                    "format": "color or grayscale",
                    "other_details": "any other relevant details"
                }
            }
            """

            # Prepare request for Nova Lite
            request_data = {
                "prompt": prompt,
                "temperature": 0.2,
                "max_tokens": 500,
                "image_base64": image_base64
            }

            # Invoke Nova Lite through Bedrock
            response = await self.bedrock_client.invoke_model(
                modelId=self.nova_model_id,
                body=json.dumps(request_data)
            )
            response_body = json.loads(await response["body"].read())

            # Extract response content - Nova Lite returns differently structured response
            response_text = response_body.get("generation", "")

            # Parse the JSON from Nova's response
            try:
                # Handle possible text before or after JSON
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_content = response_text[json_start:json_end]
                    analysis_result = json.loads(json_content)
                else:
                    # If no JSON is found, create structured data from text analysis
                    if "passport" in response_text.lower():
                        document_type = "passport"
                    elif "driver" in response_text.lower() and "license" in response_text.lower():
                        document_type = "driver's license"
                    elif "id" in response_text.lower() or "identification" in response_text.lower():
                        document_type = "identification card"
                    else:
                        document_type = "unknown document"

                    analysis_result = {
                        "document_type": document_type,
                        "image_quality": "medium",
                        "confidence": 0.7,
                        "details": {
                            "dimensions": "unknown",
                            "format": "color"
                        }
                    }

                # Ensure required fields are present
                if "document_type" not in analysis_result:
                    analysis_result["document_type"] = "unknown"
                if "image_quality" not in analysis_result:
                    analysis_result["image_quality"] = "medium"
                if "confidence" not in analysis_result:
                    analysis_result["confidence"] = 0.7
                if "details" not in analysis_result:
                    analysis_result["details"] = {}

                # Store document type in memory for future use
                self.agent_memory["document_type"] = analysis_result["document_type"]

                return analysis_result

            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response
                self.logger.warning("Failed to parse JSON from Nova's response")
                return {
                    "document_type": "unknown",
                    "image_quality": "medium",
                    "confidence": 0.5,
                    "details": {
                        "dimensions": "unknown",
                        "format": "unknown"
                    }
                }

        except Exception as e:
            self.logger.error(f"Error analyzing document with Nova: {str(e)}", exc_info=True)
            return {
                "document_type": "unknown",
                "image_quality": "unknown",
                "confidence": 0.0,
                "error": str(e)
            }

    @tool
    async def _verify_document_authenticity(self, image_base64: str, document_type: str) -> Dict:
        """Verify if a document appears authentic using Amazon Nova Lite"""
        try:
            # Get image and document type from memory if not provided directly
            if not image_base64 and "document_image" in self.agent_memory:
                image_base64 = self.agent_memory["document_image"]

            if not document_type and "document_type" in self.agent_memory:
                document_type = self.agent_memory["document_type"]

            if not image_base64:
                return {
                    "is_authentic": False,
                    "confidence": 0.0,
                    "security_features_detected": [],
                    "potential_issues": ["No image provided"]
                }

            if not document_type:
                document_type = "unknown document"

            # Prepare prompt for Nova Lite
            prompt = f"""
            You are a document authentication expert. Examine this {document_type} image carefully for authenticity.

            Look for security features that should be present in an authentic {document_type}, such as:
            - Holograms
            - Microprinting
            - Watermarks
            - Special inks or UV reactive elements
            - Proper formatting and layout
            - Official seals and signatures

            Also check for signs of tampering such as:
            - Uneven text
            - Digital manipulation artifacts
            - Inconsistent fonts
            - Misaligned elements
            - Unusual colors

            Format your response as JSON with the following structure:
            {{
                "is_authentic": true or false,
                "confidence": 0.0-1.0,
                "security_features_detected": ["feature1", "feature2"...],
                "potential_issues": ["issue1", "issue2"...]
            }}
            """

            # Prepare request for Nova Lite
            request_data = {
                "prompt": prompt,
                "temperature": 0.2,
                "max_tokens": 500,
                "image_base64": image_base64
            }

            # Invoke Nova Lite through Bedrock
            response = await self.bedrock_client.invoke_model(
                modelId=self.nova_model_id,
                body=json.dumps(request_data)
            )
            response_body = json.loads(await response["body"].read())

            # Extract response content
            response_text = response_body.get("generation", "")

            # Parse the JSON from Nova's response
            try:
                # Handle possible text before or after JSON
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_content = response_text[json_start:json_end]
                    authentication_result = json.loads(json_content)
                else:
                    raise ValueError("Could not find valid JSON in response")

                # Ensure required fields are present
                if "is_authentic" not in authentication_result:
                    authentication_result["is_authentic"] = True
                if "confidence" not in authentication_result:
                    authentication_result["confidence"] = 0.8
                if "security_features_detected" not in authentication_result:
                    authentication_result["security_features_detected"] = ["standard security features"]
                if "potential_issues" not in authentication_result:
                    authentication_result["potential_issues"] = []

                # Store authentication result in memory
                self.agent_memory["authentication_result"] = authentication_result

                return authentication_result

            except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, attempt to determine authenticity from text response
                is_authentic = "not authentic" not in response_text.lower() and "fake" not in response_text.lower()

                # Extract potential security features mentioned
                security_features = []
                if "hologram" in response_text.lower():
                    security_features.append("hologram")
                if "microprint" in response_text.lower():
                    security_features.append("microprinting")
                if "watermark" in response_text.lower():
                    security_features.append("watermark")

                # Extract potential issues mentioned
                potential_issues = []
                if "tamper" in response_text.lower():
                    potential_issues.append("signs of tampering")
                if "inconsistent" in response_text.lower():
                    potential_issues.append("inconsistent elements")

                authentication_result = {
                    "is_authentic": is_authentic,
                    "confidence": 0.7,
                    "security_features_detected": security_features if security_features else ["standard security features"],
                    "potential_issues": potential_issues
                }

                # Store authentication result in memory
                self.agent_memory["authentication_result"] = authentication_result

                return authentication_result

        except Exception as e:
            self.logger.error(f"Error verifying document authenticity: {str(e)}", exc_info=True)
            return {
                "is_authentic": False,
                "confidence": 0.0,
                "security_features_detected": [],
                "potential_issues": [f"Error during verification: {str(e)}"]
            }

    @tool
    async def _extract_document_fields(self, image_base64: str, document_type: str) -> Dict:
        """Extract fields from a document based on its type using Amazon Nova Lite"""
        try:
            # Get image and document type from memory if not provided directly
            if not image_base64 and "document_image" in self.agent_memory:
                image_base64 = self.agent_memory["document_image"]

            if not document_type and "document_type" in self.agent_memory:
                document_type = self.agent_memory["document_type"]

            if not image_base64:
                return {
                    "fields": {},
                    "confidence": {},
                    "error": "No image provided"
                }

            if not document_type:
                document_type = "unknown document"

            # Customize prompt based on document type
            field_prompts = {
                "passport": "Extract the following fields: full name, date of birth, passport number, expiry date, issuing country, nationality, gender",
                "driver's license": "Extract the following fields: full name, date of birth, license number, expiry date, issuing authority/state, address, license classes",
                "id card": "Extract the following fields: full name, date of birth, ID number, expiry date, issuing authority",
                "birth certificate": "Extract the following fields: name, date of birth, place of birth, parents' names, certificate number"
            }

            # Default prompt if document type doesn't match
            extraction_prompt = field_prompts.get(
                document_type.lower(), 
                "Extract all key fields from this document including names, dates, identification numbers, and any other relevant information"
            )

            # Prepare prompt for Nova Lite
            prompt = f"""
            {extraction_prompt}

            Review the document image carefully and extract the requested information.

            Format your response as JSON with the following structure:
            {{
                "fields": {{
                    "field_name_1": "extracted value 1",
                    "field_name_2": "extracted value 2",
                    ...
                }},
                "confidence": {{
                    "field_name_1": 0.XX,
                    "field_name_2": 0.XX,
                    ...
                }}
            }}

            Use standardized field names like: name, date_of_birth, document_number, expiry_date, issuing_country, etc.
            For each field, provide a confidence score between 0.0 and 1.0.
            """

            # Prepare request for Nova Lite
            request_data = {
                "prompt": prompt,
                "temperature": 0.2,
                "max_tokens": 1000,
                "image_base64": image_base64
            }

            # Invoke Nova Lite through Bedrock
            response = await self.bedrock_client.invoke_model(
                modelId=self.nova_model_id,
                body=json.dumps(request_data)
            )
            response_body = json.loads(await response["body"].read())

            # Extract response content
            response_text = response_body.get("generation", "")

            # Parse the JSON from Nova's response
            try:
                # Handle possible text before or after JSON
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_content = response_text[json_start:json_end]
                    extraction_result = json.loads(json_content)
                else:
                    # If no JSON structure, try to parse fields from text
                    fields = {}
                    confidences = {}

                    # Simple parsing of key-value lines
                    lines = response_text.split('\n')
                    for line in lines:
                        if ':' in line:
                            parts = line.split(':', 1)
                            key = parts[0].strip().lower().replace(' ', '_')
                            value = parts[1].strip()
                            if key and value:
                                fields[key] = value
                                confidences[key] = 0.7  # Default confidence

                    extraction_result = {
                        "fields": fields,
                        "confidence": confidences
                    }

                # Ensure required fields are present
                if "fields" not in extraction_result:
                    extraction_result["fields"] = {}
                if "confidence" not in extraction_result:
                    extraction_result["confidence"] = {}
                    # Add default confidences if missing
                    for field in extraction_result["fields"]:
                        if field not in extraction_result["confidence"]:
                            extraction_result["confidence"][field] = 0.8

                # Store extracted fields in memory for future use
                self.agent_memory["extracted_fields"] = extraction_result["fields"]

                return extraction_result

            except json.JSONDecodeError:
                # If JSON parsing fails completely, return empty with error indication
                self.logger.warning("Failed to parse fields from Nova's response")
                return {
                    "fields": {},
                    "confidence": {},
                    "error": "Could not parse fields from response"
                }

        except Exception as e:
            self.logger.error(f"Error extracting document fields: {str(e)}", exc_info=True)
            return {
                "fields": {},
                "confidence": {},
                "error": str(e)
            }

    @tool
    async def _check_document_consistency(self, fields: Dict) -> Dict:
        """Check if document fields are consistent with each other using Amazon Nova Lite"""
        try:
            # Get fields from memory if not provided directly
            if not fields and "extracted_fields" in self.agent_memory:
                fields = self.agent_memory["extracted_fields"]

            if not fields:
                return {
                    "is_consistent": False,
                    "confidence": 0.0,
                    "inconsistencies": ["No fields provided for consistency check"]
                }

            # Prepare fields for the prompt
            fields_text = "\n".join([f"{key}: {value}" for key, value in fields.items()])

            # Prepare prompt for Nova Lite
            prompt = f"""
            You are a document verification expert. Check the consistency of the following fields extracted from a document:

            {fields_text}

            Analyze these fields and check for:
            1. Inconsistencies between fields (e.g., impossible dates, conflicting information)
            2. Unusual or suspicious values
            3. Missing critical information

            Format your response as JSON with the following structure:
            {{
                "is_consistent": true or false,
                "confidence": 0.0-1.0,
                "inconsistencies": ["description of issue 1", "description of issue 2", ...]
            }}
            """

            # Prepare request for Nova Lite
            request_data = {
                "prompt": prompt,
                "temperature": 0.2,
                "max_tokens": 500
            }

            # Invoke Nova Lite through Bedrock
            response = await self.bedrock_client.invoke_model(
                modelId=self.nova_model_id,
                body=json.dumps(request_data)
            )
            response_body = json.loads(await response["body"].read())

            # Extract response content
            response_text = response_body.get("generation", "")

            # Parse the JSON from Nova's response
            try:
                # Handle possible text before or after JSON
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_content = response_text[json_start:json_end]
                    consistency_result = json.loads(json_content)
                else:
                    # Default values based on text analysis
                    is_consistent = "inconsistent" not in response_text.lower() and "issue" not in response_text.lower()

                    consistency_result = {
                        "is_consistent": is_consistent,
                        "confidence": 0.7,
                        "inconsistencies": []
                    }

                # Ensure required fields are present
                if "is_consistent" not in consistency_result:
                    consistency_result["is_consistent"] = True
                if "confidence" not in consistency_result:
                    consistency_result["confidence"] = 0.8
                if "inconsistencies" not in consistency_result:
                    consistency_result["inconsistencies"] = []

                # Store consistency result in memory
                self.agent_memory["consistency_result"] = consistency_result

                return consistency_result

            except json.JSONDecodeError:
                # If JSON parsing fails, determine consistency from response text
                is_consistent = "inconsistent" not in response_text.lower() and "issue" not in response_text.lower()

                consistency_result = {
                    "is_consistent": is_consistent,
                    "confidence": 0.6,
                    "inconsistencies": ["Could not properly analyze consistency"]
                }

                # Store consistency result in memory
                self.agent_memory["consistency_result"] = consistency_result

                return consistency_result

        except Exception as e:
            self.logger.error(f"Error checking document consistency: {str(e)}", exc_info=True)
            return {
                "is_consistent": False,
                "confidence": 0.0,
                "inconsistencies": [f"Error during consistency check: {str(e)}"]
            }
