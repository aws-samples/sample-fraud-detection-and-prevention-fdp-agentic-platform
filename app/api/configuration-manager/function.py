# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Configuration Manager"""

# configuration-manager/function.py
import json
import logging
from dotenv import load_dotenv
from lib.utils import create_api_response
from lib.dynamodb import DynamoDBService
from lib.models import Configuration
from lib.configuration_manager import ConfigurationManager

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
MANAGER = ConfigurationManager(SERVICES, LOGGER)

async def get_configurations(event, context):
    """GET method for /configurations/{config_id}"""
    LOGGER.info("Received get configurations request")

    try:
        if event.get('httpMethod') == 'OPTIONS':
            return create_api_response(200, {})

        config_id = event['pathParameters']['config_id']
        results = await MANAGER.get_configurations(config_id)
        return create_api_response(200, results)
    except Exception as e: # pylint: disable=broad-except
        LOGGER.error("Error: %s", str(e))
        return create_api_response(500, {'detail': str(e)})

async def update_configuration(event, context):
    """PUT method for /configurations"""
    LOGGER.info("Received update configuration request")

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
        config_data = Configuration(**body).dict(exclude_unset=True)

        result = await MANAGER.update_configuration(config_data)
        return create_api_response(200, result)
    except ValueError as ve:
        return create_api_response(400, {'detail': str(ve)})
    except Exception as e: # pylint: disable=broad-except
        LOGGER.error("Error: %s", str(e))
        return create_api_response(500, {'detail': str(e)})

async def get_active_model(event, context):
    """GET method for /configurations/model/active"""
    LOGGER.info("Received get active model request")

    try:
        if event.get('httpMethod') == 'OPTIONS':
            return create_api_response(200, {})

        result = await MANAGER.get_active_model_config()
        if not result:
            return create_api_response(404, {'detail': 'No active model configuration found'})
        return create_api_response(200, result)
    except Exception as e: # pylint: disable=broad-except
        LOGGER.error("Error: %s", str(e))
        return create_api_response(500, {'detail': str(e)})

async def get_inference_params(event, context):
    """GET method for /configurations/inference-params"""
    LOGGER.info("Received get inference parameters request")

    try:
        if event.get('httpMethod') == 'OPTIONS':
            return create_api_response(200, {})

        results = await MANAGER.get_inference_params()
        return create_api_response(200, results)
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
    if http_method == 'GET' and path.startswith('/configurations/model/active'):
        return get_active_model(event, context)
    if http_method == 'GET' and path.startswith('/configurations/inference-params'):
        return get_inference_params(event, context)
    if http_method == 'GET' and path.startswith('/configurations'):
        return get_configurations(event, context)
    if http_method == 'PUT' and path.startswith('/configurations'):
        return update_configuration(event, context)

    return create_api_response(404, {'detail': 'Not Found'})
