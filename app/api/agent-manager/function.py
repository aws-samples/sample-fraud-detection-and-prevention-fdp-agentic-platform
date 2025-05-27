# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Agent Manager"""

# agent-manager/function.py
import json
import logging
import os
import boto3
from dotenv import load_dotenv
from lib.utils import create_api_response
from lib.dynamodb import DynamoDBService
from lib.s3 import S3Service
from lib.models import DocumentAnalysisRequest
from lib.document_analyzer import DocumentAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def initialize_services():
    """Initialize services at module level"""
    if not os.environ.get('FDP_S3_BUCKET'):
        raise ValueError("FDP_S3_BUCKET environment variable is not set")

    bedrock_client = boto3.client(
        "bedrock-runtime",
        region_name="us-east-1",
    )
    s3_service = S3Service()
    db_service = DynamoDBService()

    return {
        'bedrock_client': bedrock_client,
        's3_service': s3_service,
        'db_service': db_service
    }

# Initialize services at module level
SERVICES = initialize_services()

# Initialize analyzer at module level
MANAGER = DocumentAnalyzer(SERVICES, LOGGER)

async def create_verifications(event, context):
    """POST method for /verifications"""
    LOGGER.info("Received create verifications request")

    try:
        if event.get('httpMethod') == 'OPTIONS':
            return create_api_response(200, {})

        # Parse request body
        body = event.get('body')
        if not body:
            return create_api_response(400, {'detail': 'No body found in request'})

        if isinstance(body, str):
            body = json.loads(body)

        request = DocumentAnalysisRequest(**body)

        # Process document
        result = await MANAGER.analyze_document(request.image_base64)
        return create_api_response(200, result)

    except ValueError as ve:
        LOGGER.error("Validation error: %s", str(ve))
        return create_api_response(400, {'detail': str(ve)})
    except Exception as e: # pylint: disable=broad-except
        LOGGER.error("Error: %s", str(e))
        return create_api_response(500, {'detail': str(e)})

async def get_verifications(event, context):
    """GET method for /verifications"""
    LOGGER.info("Received get verifications request")

    try:
        if event.get('httpMethod') == 'OPTIONS':
            return create_api_response(200, {})

        if 'pathParameters' in event and 'verification_id' in event['pathParameters']:
            verification_id = event['pathParameters']['verification_id']
            result = await MANAGER.get_verification(verification_id)
        else:
            result = await MANAGER.get_verifications()
        return create_api_response(200, result)

    except ValueError as ve:
        return create_api_response(404, {'detail': str(ve)})
    except Exception as e: # pylint: disable=broad-except
        LOGGER.error("Error: %s", str(e))
        return create_api_response(500, {'detail': str(e)})

def handler(event, context):
    """Main handler function for Lambda"""
    LOGGER.info("Received event: %s", json.dumps(event))

    # Get HTTP method and path
    http_method = event['httpMethod']
    path = event['path']

    # Route requests to appropriate handler
    if http_method == 'GET' and path.startswith('/verifications'):
        return get_verifications(event, context)
    if http_method == 'POST' and path.startswith('/verifications'):
        return create_verifications(event, context)

    return create_api_response(404, {'detail': 'Not Found'})

if __name__ == '__main__':
    handler(event=None, context=None)
