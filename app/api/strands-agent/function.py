# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Strands Agent for Document Verification"""

import json
import logging
from dotenv import load_dotenv
import boto3
import asyncio
from lib.utils import create_api_response
from lib.document_verification_agent import DocumentVerificationAgent
from lib.models import AgentRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def initialize_services():
    """Initialize services at module level"""

    # Import these here to avoid circular imports
    from lib.dynamodb import DynamoDBService
    from lib.s3 import S3Service

    bedrock_client = boto3.client("bedrock-runtime")
    s3_service = S3Service()
    db_service = DynamoDBService()

    return {
        'bedrock_client': bedrock_client,
        's3_service': s3_service,
        'db_service': db_service
    }

# Initialize services at module level
SERVICES = initialize_services()

# Initialize agent at module level
AGENT = DocumentVerificationAgent(SERVICES, LOGGER)

async def start_verification(event, context):
    """POST method for /strands"""
    LOGGER.info("Received start verification request")

    try:
        if event.get('httpMethod') == 'OPTIONS':
            return create_api_response(200, {})

        # Parse request body
        body = event.get('body')
        if not body:
            return create_api_response(400, {'detail': 'No body found in request'})

        if isinstance(body, str):
            body = json.loads(body)

        request = AgentRequest(**body)

        # Start the verification process
        result = await AGENT.start_verification(request)
        return create_api_response(200, result)

    except ValueError as ve:
        LOGGER.error("Validation error: %s", str(ve))
        return create_api_response(400, {'detail': str(ve)})
    except Exception as e:
        LOGGER.error("Error: %s", str(e), exc_info=True)
        return create_api_response(500, {'detail': str(e)})

async def get_verification_status(event, context):
    """GET method for /strands/{verification_id}"""
    LOGGER.info("Received get verification status request")

    try:
        if event.get('httpMethod') == 'OPTIONS':
            return create_api_response(200, {})

        # Get verification_id from path parameters
        path_params = event.get('pathParameters') or {}
        verification_id = path_params.get('verification_id')
        
        if not verification_id:
            return create_api_response(400, {'detail': 'No verification_id found in request'})

        # Get verification status
        result = await AGENT.get_verification_status(verification_id)
        if not result:
            return create_api_response(404, {'detail': 'Verification not found'})
        
        return create_api_response(200, result)

    except Exception as e:
        LOGGER.error("Error: %s", str(e), exc_info=True)
        return create_api_response(500, {'detail': str(e)})

async def provide_additional_info(event, context):
    """PUT method for /strands/{verification_id}"""
    LOGGER.info("Received provide additional info request")

    try:
        if event.get('httpMethod') == 'OPTIONS':
            return create_api_response(200, {})

        # Get verification_id from path parameters
        path_params = event.get('pathParameters') or {}
        verification_id = path_params.get('verification_id')
        
        if not verification_id:
            return create_api_response(400, {'detail': 'No verification_id found in request'})

        # Parse request body
        body = event.get('body')
        if not body:
            return create_api_response(400, {'detail': 'No body found in request'})

        if isinstance(body, str):
            body = json.loads(body)

        # Process additional information
        result = await AGENT.provide_additional_info(verification_id, body)
        return create_api_response(200, result)

    except Exception as e:
        LOGGER.error("Error: %s", str(e), exc_info=True)
        return create_api_response(500, {'detail': str(e)})

def handler(event, context):
    """Main handler function for Lambda"""
    LOGGER.info("Received event: %s", json.dumps(event))

    # Get HTTP method and path
    http_method = event['httpMethod']
    path = event['path']

    # Create a new event loop for each request
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Route requests to appropriate handler
        if http_method == 'POST' and path.endswith('/strands'):
            # Create a fresh coroutine object
            coro = start_verification(event, context)
            result = loop.run_until_complete(coro)
            return result
        elif http_method == 'GET' and '/strands/' in path:
            # Create a fresh coroutine object
            coro = get_verification_status(event, context)
            result = loop.run_until_complete(coro)
            return result
        elif http_method == 'PUT' and '/strands/' in path:
            # Create a fresh coroutine object
            coro = provide_additional_info(event, context)
            result = loop.run_until_complete(coro)
            return result

        return create_api_response(404, {'detail': 'Not Found'})
    except Exception as e:
        LOGGER.error("Error processing request: %s", str(e), exc_info=True)
        return create_api_response(500, {'detail': str(e)})
    finally:
        # Clean up the event loop
        loop.close()

if __name__ == '__main__':
    handler(event=None, context=None)
