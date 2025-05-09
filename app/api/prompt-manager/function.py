# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Prompt Manager Function"""

# prompt-manager/function.py
import json
import logging
from dotenv import load_dotenv
from lib.utils import create_api_response
from lib.dynamodb import DynamoDBService
from lib.models import Prompt
from lib.prompt_manager import PromptManager

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def initialize_services():
    """Initialize services at module level"""
    db_service = DynamoDBService()
    return {
        'db_service': db_service
    }

# Initialize services at module level
SERVICES = initialize_services()

# Initialize manager at module level
MANAGER = PromptManager(SERVICES, LOGGER)

async def get_prompts(event, context):
    """GET method for /prompts"""
    LOGGER.info("Received get prompts request")

    try:
        if event.get('httpMethod') == 'OPTIONS':
            return create_api_response(200, {})

        results = await MANAGER.get_prompts()
        return create_api_response(200, results)
    except Exception as e: # pylint: disable=broad-except
        LOGGER.error("Error: %s", str(e))
        return create_api_response(500, {'detail': str(e)})

async def create_prompt(event, context):
    """POST method for /prompts"""
    LOGGER.info("Received create prompt request")

    try:
        if event.get('httpMethod') == 'OPTIONS':
            return create_api_response(200, {})

        # Parse request body
        body = event.get('body')
        if not body:
            return create_api_response(400, {'detail': 'No body found in request'})

        if isinstance(body, str):
            body = json.loads(body)

        # Validate through pydantic model
        prompt_data = Prompt(**body).dict(exclude_unset=True)

        result = await MANAGER.create_prompt(prompt_data)
        return create_api_response(201, result)
    except ValueError as ve:
        return create_api_response(400, {'detail': str(ve)})
    except Exception as e: # pylint: disable=broad-except
        LOGGER.error("Error: %s", str(e))
        return create_api_response(500, {'detail': str(e)})

async def update_prompt(event, context):
    """PUT method for /prompts/{prompt_id}"""
    LOGGER.info("Received update prompt request")

    try:
        if event.get('httpMethod') == 'OPTIONS':
            return create_api_response(200, {})

        # Get path parameters
        prompt_id = event['pathParameters']['prompt_id']

        # Parse request body
        body = event.get('body')
        if not body:
            return create_api_response(400, {'detail': 'No body found in request'})

        if isinstance(body, str):
            body = json.loads(body)

        # Validate through pydantic model
        prompt_data = Prompt(**body).dict(exclude_unset=True)

        result = await MANAGER.update_prompt(prompt_id, prompt_data)
        return create_api_response(200, result)
    except ValueError as ve:
        return create_api_response(404, {'detail': str(ve)})
    except Exception as e: # pylint: disable=broad-except
        LOGGER.error("Error: %s", str(e))
        return create_api_response(500, {'detail': str(e)})

async def delete_prompt(event, context):
    """DELETE method for /prompts/{prompt_id}"""
    LOGGER.info("Received delete prompt request")

    try:
        if event.get('httpMethod') == 'OPTIONS':
            return create_api_response(200, {})

        prompt_id = event['pathParameters']['prompt_id']
        await MANAGER.delete_prompt(prompt_id)
        return create_api_response(200, {'message': 'Prompt deleted'})
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
    if http_method == 'GET' and path.startswith('/prompts'):
        return get_prompts(event, context)
    if http_method == 'POST' and path.startswith('/prompts'):
        return create_prompt(event, context)
    if http_method == 'PUT' and path.startswith('/prompts'):
        return update_prompt(event, context)
    if http_method == 'DELETE' and path.startswith('/prompts'):
        return delete_prompt(event, context)

    return create_api_response(404, {'detail': 'Not Found'})
