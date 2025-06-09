# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""DynamoDB extensions for Strands Agent"""

import boto3
import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentDynamoDBService:
    """DynamoDB service extensions for Strands Agent"""

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.agent_verifications_table_name = os.getenv('FDP_DDB_STRANDS')

        # Initialize table reference
        self.agent_verifications_table = self.ensure_agent_verifications_table_exists()

    def ensure_agent_verifications_table_exists(self):
        """Create the agent verifications DynamoDB table if it doesn't exist"""
        try:
            table = self.dynamodb.Table(self.agent_verifications_table_name)
            table.meta.client.describe_table(TableName=self.agent_verifications_table_name)
            logger.info(f"Agent verifications table exists: {self.agent_verifications_table_name}")
            return table
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info(f"Creating agent verifications table: {self.agent_verifications_table_name}")
                table = self.dynamodb.create_table(
                    TableName=self.agent_verifications_table_name,
                    KeySchema=[
                        {
                            'AttributeName': 'verification_id',
                            'KeyType': 'HASH'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'verification_id',
                            'AttributeType': 'S'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )

                table.meta.client.get_waiter('table_exists').wait(TableName=self.agent_verifications_table_name)
                logger.info(f"Agent verifications table created successfully: {self.agent_verifications_table_name}")
                return table
            else:
                logger.error(f"Error checking/creating agent verifications table: {repr(e)}")
                raise

    async def save_agent_verification(self, verification: Dict) -> Dict:
        """Save a new agent verification"""
        try:
            current_time = datetime.now(timezone.utc).isoformat()
            if 'created_at' not in verification:
                verification['created_at'] = current_time
            verification['updated_at'] = current_time

            self.agent_verifications_table.put_item(Item=verification)
            return verification
        except Exception as e:
            logger.error(f"Error saving agent verification: {repr(e)}")
            raise

    async def update_agent_verification(self, verification: Dict) -> Dict:
        """Update an existing agent verification"""
        try:
            verification['updated_at'] = datetime.now(timezone.utc).isoformat()
            self.agent_verifications_table.put_item(Item=verification)
            return verification
        except Exception as e:
            logger.error(f"Error updating agent verification: {repr(e)}")
            raise

    async def get_agent_verification(self, verification_id: str) -> Optional[Dict]:
        """Get a specific agent verification by ID"""
        try:
            logger.info(f"Getting agent verification with id: {verification_id}")
            response = self.agent_verifications_table.get_item(
                Key={'verification_id': verification_id}
            )

            item = response.get('Item')
            if not item:
                logger.warning(f"Agent verification with id {verification_id} not found")
                return None

            return item
        except Exception as e:
            logger.error(f"Error getting agent verification: {repr(e)}")
            raise

    async def get_agent_verifications(self) -> List[Dict]:
        """Get all agent verifications"""
        try:
            logger.info(f"Scanning agent verifications table: {self.agent_verifications_table_name}")
            items = []
            last_evaluated_key = None

            while True:
                scan_kwargs = {}
                if last_evaluated_key:
                    scan_kwargs['ExclusiveStartKey'] = last_evaluated_key

                response = self.agent_verifications_table.scan(**scan_kwargs)
                items.extend(response.get('Items', []))

                last_evaluated_key = response.get('LastEvaluatedKey')
                if not last_evaluated_key:
                    break

            logger.info(f"Retrieved {len(items)} agent verifications")
            return items
        except Exception as e:
            logger.error(f"Error getting agent verifications: {repr(e)}")
            raise

# Extend the DynamoDBService class with agent verification methods
def extend_dynamodb_service(db_service):
    """Extend the DynamoDBService class with agent verification methods"""
    agent_db_service = AgentDynamoDBService()

    # Add agent verification methods to the DynamoDBService instance
    db_service.save_agent_verification = agent_db_service.save_agent_verification
    db_service.update_agent_verification = agent_db_service.update_agent_verification
    db_service.get_agent_verification = agent_db_service.get_agent_verification
    db_service.get_agent_verifications = agent_db_service.get_agent_verifications

    return db_service
