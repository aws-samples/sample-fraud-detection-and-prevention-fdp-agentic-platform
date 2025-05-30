# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# lib/dynamodb.py
import boto3
from datetime import datetime, timezone
from typing import Dict, List, Optional
from decimal import Decimal
import os
from dotenv import load_dotenv
import logging
from .s3 import S3Service
from botocore.exceptions import ClientError
import uuid
from .models import Configuration
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DynamoDBService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.agent_table_name = os.getenv('FDP_DDB_AGENT')
        self.prompts_table_name = os.getenv('FDP_DDB_PROMPT')
        self.configs_table_name = os.getenv('FDP_DDB_CONFIG')
        self.s3_bucket_name = os.getenv('FDP_S3_BUCKET')

        if not self.s3_bucket_name:
            raise ValueError("FDP_S3_BUCKET environment variable is not set")

        # Initialize services
        self.s3_service = S3Service()

        # Initialize table references
        self.verifications_table = self.ensure_table_exists()
        self.prompts_table = self.ensure_prompts_table_exists()
        self.configs_table = self.ensure_configs_table_exists()

    def ensure_table_exists(self):
        """Create the DynamoDB table if it doesn't exist"""
        try:
            table = self.dynamodb.Table(self.agent_table_name)
            table.load()
            logger.info(f"Table exists: {self.agent_table_name}")
            return table
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info(f"Creating table: {self.agent_table_name}")
                table = self.dynamodb.create_table(
                    TableName=self.agent_table_name,
                    KeySchema=[
                        {
                            'AttributeName': 'pk',
                            'KeyType': 'HASH'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'pk',
                            'AttributeType': 'S'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )

                table.meta.client.get_waiter('table_exists').wait(TableName=self.agent_table_name)
                logger.info(f"Table created successfully: {self.agent_table_name}")
                return table
            else:
                logger.error(f"Error checking/creating table: {repr(e)}")
                raise

    def ensure_prompts_table_exists(self):
        """Create the prompts DynamoDB table if it doesn't exist"""
        try:
            table = self.dynamodb.Table(self.prompts_table_name)
            table.meta.client.describe_table(TableName=self.prompts_table_name)
            logger.info(f"Prompts table exists: {self.prompts_table_name}")
            return table
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info(f"Creating prompts table: {self.prompts_table_name}")
                table = self.dynamodb.create_table(
                    TableName=self.prompts_table_name,
                    KeySchema=[
                        {
                            'AttributeName': 'pk',
                            'KeyType': 'HASH'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'pk',
                            'AttributeType': 'S'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )

                table.meta.client.get_waiter('table_exists').wait(TableName=self.prompts_table_name)
                logger.info(f"Prompts table created successfully: {self.prompts_table_name}")
                return table
            else:
                logger.error(f"Error checking/creating prompts table: {repr(e)}")
                raise

    def ensure_configs_table_exists(self):
        """Create the configurations DynamoDB table if it doesn't exist"""
        try:
            table = self.dynamodb.Table(self.configs_table_name)
            table.meta.client.describe_table(TableName=self.configs_table_name)
            logger.info(f"Configs table exists: {self.configs_table_name}")
            return table
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info(f"Creating configs table: {self.configs_table_name}")
                table = self.dynamodb.create_table(
                    TableName=self.configs_table_name,
                    KeySchema=[
                        {
                            'AttributeName': 'pk',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'key',
                            'KeyType': 'RANGE'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'pk',
                            'AttributeType': 'S'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )

                table.meta.client.get_waiter('table_exists').wait(TableName=self.configs_table_name)
                logger.info(f"Configs table created successfully: {self.configs_table_name}")

                # Initialize with default values
                self.initialize_default_configs()
                return table
            else:
                logger.error(f"Error checking/creating configs table: {repr(e)}")
                raise

    def initialize_default_configs(self):
        """Initialize the configs table with default values"""
        try:
            # Model IDs configurations
            model_configs = [
                {
                    'pk': 'MODEL_IDS',
                    'key': 'MICRO',
                    'value': 'amazon.nova-micro-v1:0',
                    'description': 'Micro Model ID',
                    'is_active': False
                },
                {
                    'pk': 'MODEL_IDS',
                    'key': 'LITE',
                    'value': 'amazon.nova-lite-v1:0',
                    'description': 'Lite Model ID',
                    'is_active': True
                },
                {
                    'pk': 'MODEL_IDS',
                    'key': 'PRO',
                    'value': 'amazon.nova-pro-v1:0',
                    'description': 'Pro Model ID',
                    'is_active': False
                }
            ]

            # Inference parameters configurations
            inference_configs = [
                {
                    'pk': 'INFERENCE_PARAMS',
                    'key': 'max_new_tokens',
                    'value': '3000',
                    'description': 'Maximum number of new tokens'
                },
                {
                    'pk': 'INFERENCE_PARAMS',
                    'key': 'top_p',
                    'value': '0.1',
                    'description': 'Top P value'
                },
                {
                    'pk': 'INFERENCE_PARAMS',
                    'key': 'top_k',
                    'value': '20',
                    'description': 'Top K value'
                },
                {
                    'pk': 'INFERENCE_PARAMS',
                    'key': 'temperature',
                    'value': '0.3',
                    'description': 'Temperature value'
                }
            ]

            # Write all configurations to the table using batch writer
            current_time = datetime.now(timezone.utc).isoformat()
            with self.configs_table.batch_writer() as batch:
                for config in model_configs + inference_configs:
                    config['created_at'] = current_time
                    config['updated_at'] = current_time
                    batch.put_item(Item=config)

            logger.info("Default configurations initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing default configurations: {repr(e)}")
            raise

    async def save_verification(self, verification_data: Dict) -> Dict:
        """Save a verification record with optimized handling"""
        try:
            aware_datetime = datetime.now(timezone.utc)
            timestamp = aware_datetime.isoformat()

            # Convert confidence to Decimal for DynamoDB
            confidence = Decimal(str(verification_data.get('confidence', 0)))

            # Create item for DynamoDB
            item = {
                'pk': verification_data.get('id'),
                'timestamp': timestamp,
                'document_type': verification_data.get('document_type'),
                'confidence': confidence,
                'content_text': verification_data.get('content_text'),
                'file_key': verification_data.get('file_key')
            }

            # Validate required fields
            missing_fields = [key for key, value in item.items() if value is None]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

            # Save to DynamoDB
            self.verifications_table.put_item(Item=item)

            # Process item for response
            response_item = item.copy()
            response_item['confidence'] = float(response_item['confidence'])

            # Generate a fresh presigned URL if file exists
            if response_item.get('file_key'):
                response_item['preview_url'] = self.s3_service.get_presigned_url(response_item['file_key'])

            logger.info(f"Successfully saved verification: {response_item['pk']}")
            return response_item

        except Exception as e:
            logger.error(f"Error saving verification: {repr(e)}")
            raise

    async def get_verifications(self) -> List[Dict]:
        """Get all verifications with pagination support"""
        try:
            logger.info(f"Scanning table: {self.agent_table_name}")
            items = []
            last_evaluated_key = None

            while True:
                scan_kwargs = {}
                if last_evaluated_key:
                    scan_kwargs['ExclusiveStartKey'] = last_evaluated_key

                response = self.verifications_table.scan(**scan_kwargs)
                items.extend(response.get('Items', []))

                last_evaluated_key = response.get('LastEvaluatedKey')
                if not last_evaluated_key:
                    break

            processed_items = []
            for item in items:
                processed_item = {
                    'pk': item.get('id'),
                    'timestamp': item.get('timestamp'),
                    'document_type': item.get('document_type'),
                    'confidence': float(item.get('confidence', 0)),
                    'content_text': item.get('content_text', ''),
                    'file_key': item.get('file_key'),
                    'preview_url': None
                }

                if processed_item['file_key']:
                    try:
                        processed_item['preview_url'] = self.s3_service.get_presigned_url(
                            processed_item['file_key']
                        )
                    except Exception as e:
                        logger.error(f"Error generating preview URL: {repr(e)}")

                processed_items.append(processed_item)
            
            logger.info(f"Processed {len(processed_items)} verifications")
            return processed_items

        except Exception as e:
            logger.error(f"Error in get_verifications: {repr(e)}", exc_info=True)
            raise

    async def deactivate_prompt(self, prompt_id: str):
        """Deactivate a prompt without optimistic locking"""
        try:
            prompt = await self.get_prompt(prompt_id)
            if prompt and prompt.get('is_active'):
                prompt['is_active'] = False
                prompt['updated_at'] = datetime.now(timezone.utc).isoformat()
                # Direct put_item without conditional expression
                self.prompts_table.put_item(Item=prompt)
                logger.info(f"Successfully deactivated prompt {prompt_id}")
        except Exception as e:
            logger.error(f"Error deactivating prompt: {repr(e)}")
            raise

    async def _deactivate_other_prompts(self, current_prompt_id: Optional[str] = None):
        """Helper method to deactivate all prompts except the current one"""
        try:
            response = self.prompts_table.scan(
                FilterExpression='is_active = :true',
                ExpressionAttributeValues={':true': True}
            )

            for prompt in response.get('Items', []):
                if prompt['pk'] != current_prompt_id:
                    await self.deactivate_prompt(prompt['pk'])

            logger.info(f"Successfully deactivated other prompts except {repr(current_prompt_id)}")
        except Exception as e:
            logger.error(f"Error deactivating prompts: {repr(e)}")
            raise

    async def get_prompts(self) -> List[Dict]:
        """Get all prompts with pagination support"""
        try:
            logger.info(f"Scanning prompts table: {self.prompts_table_name}")
            items = []
            last_evaluated_key = None

            while True:
                scan_kwargs = {}
                if last_evaluated_key:
                    scan_kwargs['ExclusiveStartKey'] = last_evaluated_key

                response = self.prompts_table.scan(**scan_kwargs)
                items.extend(response.get('Items', []))

                last_evaluated_key = response.get('LastEvaluatedKey')
                if not last_evaluated_key:
                    break

            logger.info(f"Retrieved {len(items)} prompts")
            return items
        except Exception as e:
            logger.error(f"Error getting prompts: {repr(e)}")
            raise

    async def get_prompt(self, prompt_id: str) -> Dict:
        """Get a specific prompt by ID"""
        try:
            logger.info(f"Getting prompt with id: {prompt_id}")
            response = self.prompts_table.get_item(
                Key={'pk': prompt_id}
            )

            item = response.get('Item')
            if not item:
                logger.warning(f"Prompt with id {prompt_id} not found")
                return None

            return item
        except Exception as e:
            logger.error(f"Error getting prompt: {repr(e)}")
            raise

    async def save_prompt(self, prompt: Dict) -> Dict:
        """Save a new prompt with optimistic locking"""
        try:
            current_time = datetime.now(timezone.utc).isoformat()
            item = {
                'pk': str(uuid.uuid4()),
                'role': prompt['role'],
                'tasks': prompt['tasks'],
                'is_active': prompt['is_active'],
                'created_at': current_time,
                'updated_at': current_time
            }

            # If this prompt is being set as active, deactivate others first
            if prompt['is_active']:
                await self._deactivate_other_prompts(item['pk'])

            logger.info(f"Saving new prompt with id: {item['pk']}")
            self.prompts_table.put_item(
                Item=item,
                ConditionExpression='attribute_not_exists(pk)'
            )
            return item
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError("Prompt ID already exists")
            logger.error(f"Error saving prompt: {repr(e)}")
            raise
        except Exception as e:
            logger.error(f"Error saving prompt: {repr(e)}")
            raise

    async def update_prompt_without_locking(self, prompt_data: Dict) -> Dict:
        """Update an existing prompt without optimistic locking"""
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            item = {
                'pk': prompt_data['pk'],
                'role': prompt_data['role'],
                'tasks': prompt_data['tasks'],
                'is_active': prompt_data['is_active'],
                'created_at': prompt_data.get('created_at'),
                'updated_at': timestamp
            }

            logger.info(f"Updating prompt without locking, id: {item['pk']}")
            self.prompts_table.put_item(Item=item)
            return item
        except Exception as e:
            logger.error(f"Error updating prompt without locking: {repr(e)}")
            raise

    async def delete_prompt(self, prompt_id: str):
        """Delete a prompt with validation"""
        try:
            logger.info(f"Deleting prompt with id: {repr(prompt_id)}")
            self.prompts_table.delete_item(
                Key={'pk': prompt_id},
                ConditionExpression='attribute_exists(pk)'
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError("Prompt does not exist")
            logger.error(f"Error deleting prompt: {repr(e)}")
            raise
        except Exception as e:
            logger.error(f"Error deleting prompt: {repr(e)}")
            raise

    @lru_cache(maxsize=1)
    async def get_active_prompt(self):
        """Get the currently active prompt with caching"""
        try:
            response = self.prompts_table.scan(
                FilterExpression='is_active = :true',
                ExpressionAttributeValues={':true': True}
            )

            items = response.get('Items', [])
            if not items:
                logger.warning("No active prompt found")
                return None
            
            if len(items) > 1:
                logger.warning("Multiple active prompts found, using the first one")

            return items[0]
        except Exception as e:
            logger.error(f"Error getting active prompt: {repr(e)}")
            raise

    async def get_configurations(self, config_id: str):
        """Get all configurations for a specific ID with error handling"""
        try:
            response = self.configs_table.query(
                KeyConditionExpression='pk = :pk',
                ExpressionAttributeValues={':pk': config_id}
            )
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Error getting configurations: {repr(e)}")
            raise

    async def update_configuration(self, config: Configuration):
        """Update a configuration value with optimistic locking"""
        try:
            config_dict = config.dict()
            current_time = datetime.now(timezone.utc).isoformat()
            config_dict['updated_at'] = current_time

            condition_expression = (
                'attribute_not_exists(pk) OR '
                'attribute_not_exists(updated_at) OR '
                'updated_at = :old_timestamp'
            )

            self.configs_table.put_item(
                Item=config_dict,
                ConditionExpression=condition_expression,
                ExpressionAttributeValues={
                    ':old_timestamp': config_dict.get('updated_at', current_time)
                }
            )
            return config_dict
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError("Configuration was updated by another process")
            logger.error(f"Error updating configuration: {repr(e)}")
            raise
        except Exception as e:
            logger.error(f"Error updating configuration: {repr(e)}")
            raise

    @lru_cache(maxsize=1)
    async def get_active_model_config(self):
        """Get the currently active model configuration with caching"""
        try:
            response = self.configs_table.query(
                KeyConditionExpression='pk = :pk',
                FilterExpression='is_active = :true',
                ExpressionAttributeValues={
                    ':pk': 'MODEL_IDS',
                    ':true': True
                }
            )

            items = response.get('Items', [])
            if not items:
                # If no active model, return the LITE model as default
                response = self.configs_table.query(
                    KeyConditionExpression='pk = :pk AND #key = :key',
                    ExpressionAttributeNames={'#key': 'key'},
                    ExpressionAttributeValues={
                        ':pk': 'MODEL_IDS',
                        ':key': 'LITE'
                    }
                )
                return response['Items'][0] if response['Items'] else None

            return items[0]
        except Exception as e:
            logger.error(f"Error getting active model config: {repr(e)}")
            raise

    def clear_caches(self):
        """Clear all cached data"""
        self.get_active_prompt.cache_clear()
        self.get_active_model_config.cache_clear()
