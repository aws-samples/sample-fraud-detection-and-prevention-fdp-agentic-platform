# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Document Analyzer"""

# lib/agent-manager.py
import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from utils import extract_confidence_score, extract_document_type

class DocumentAnalyzer:
    """Document Analyzer"""
    def __init__(self, services, logger):
        self.db_service = services['db_service']
        self.s3_service = services['s3_service']
        self.bedrock_client = services['bedrock_client']
        self.logger = logger

    async def analyze_document(self, image_base64: str):
        """Main business logic for document analysis"""
        # Get active configurations
        active_prompt = await self.db_service.get_active_prompt()
        if not active_prompt:
            raise ValueError('No active prompt configured')

        active_model = await self.db_service.get_active_model_config()
        if not active_model:
            raise ValueError('No active model configured')

        # Get inference configurations
        inference_configs = await self._get_inference_configs()

        # Upload to S3
        file_key = self.s3_service.upload_base64_image(image_base64)
        self.logger.info(f"Image uploaded with key: {file_key}")

        # Get model response
        content_text = await self._invoke_model(
            image_base64,
            active_prompt,
            active_model,
            inference_configs
        )

        # Process and save results
        return await self._process_and_save_results(content_text, file_key)

    async def get_verifications(self):
        """Retrieve all verifications"""
        raw_verifications = await self.db_service.get_verifications()
        return [
            self._process_verification(verification)
            for verification in raw_verifications
        ]

    async def get_verification(self, verification_id: str):
        """Retrieve specific verification"""
        verification = await self.db_service.get_verification(verification_id)
        if not verification:
            raise ValueError("Verification not found")
        return self._process_verification(verification)

    async def _get_inference_configs(self):
        """Get and process inference configurations"""
        configs = await self.db_service.get_configurations('INFERENCE_PARAMS')
        return {
            config['key']: float(config['value'])
            for config in configs
        }

    async def _invoke_model(self, image_base64, active_prompt, active_model, inference_configs):
        """Invoke Bedrock model and get response"""
        native_request = {
            "schemaVersion": "messages-v1",
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": "png",
                            "source": {"bytes": image_base64},
                        }
                    },
                    {
                        "text": active_prompt['tasks']
                    }
                ],
            }],
            "system": [{"text": active_prompt['role']}],
            "inferenceConfig": {
                "max_new_tokens": int(inference_configs.get('max_new_tokens', 3000)),
                "top_p": inference_configs.get('top_p', 0.1),
                "top_k": int(inference_configs.get('top_k', 20)),
                "temperature": inference_configs.get('temperature', 0.3)
            },
        }

        response = self.bedrock_client.invoke_model(
            modelId=active_model['value'],
            body=json.dumps(native_request)
        )

        model_response = json.loads(response["body"].read())
        return model_response["output"]["message"]["content"][0]["text"]

    async def _process_and_save_results(self, content_text, file_key):
        """Process model response and save verification"""
        confidence_score = extract_confidence_score(content_text)
        document_type = extract_document_type(content_text)

        verification_data = {
            'id': str(uuid.uuid4()),
            'document_type': document_type,
            'confidence': Decimal(str(confidence_score)),
            'content_text': content_text,
            'file_key': file_key,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        saved_verification = await self.db_service.save_verification(verification_data)
        preview_url = self.s3_service.get_presigned_url(file_key)

        return {
            'id': saved_verification['id'],
            'timestamp': saved_verification['timestamp'],
            'document_type': document_type,
            'confidence': float(saved_verification['confidence']),
            'content_text': content_text,
            'file_key': file_key,
            'preview_url': preview_url
        }

    def _process_verification(self, verification):
        """Process a verification record for response"""
        if isinstance(verification.get('confidence'), Decimal):
            verification['confidence'] = float(verification['confidence'])

        if verification.get('file_key'):
            verification['preview_url'] = self.s3_service.get_presigned_url(
                verification['file_key']
            )

        return verification
