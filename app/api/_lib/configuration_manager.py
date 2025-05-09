# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Configuration Manager"""

# lib/configuration-manager.py
from datetime import datetime, timezone

class ConfigurationManager:
    """Configuration Manager"""
    def __init__(self, services, logger):
        self.db_service = services['db_service']
        self.logger = logger

    async def get_configurations(self, config_id: str):
        """Retrieve configurations by config_id"""
        try:
            configs = await self.db_service.get_configurations(config_id)
            if not configs:
                self.logger.warning(f"No configurations found for config_id: {config_id}")
                return []
            return configs
        except Exception as e:
            self.logger.error(f"Error retrieving configurations: {str(e)}")
            raise

    async def update_configuration(self, config_data: dict):
        """Update configuration"""
        try:
            # Validate configuration exists
            existing_configs = await self.db_service.get_configurations(config_data['id'])
            existing_config = next(
                (c for c in existing_configs if c['key'] == config_data['key']),
                None
            )

            if not existing_config:
                return await self._create_configuration(config_data)

            # Update metadata
            config_data['updated_at'] = datetime.now(timezone.utc).isoformat()
            config_data['created_at'] = existing_config.get('created_at')

            # If this config is being set as active, handle activation logic
            if config_data.get('is_active'):
                await self._handle_config_activation(
                    config_data['id'],
                    config_data['key']
                )

            return await self.db_service.update_configuration(config_data)
        except Exception as e:
            self.logger.error(f"Error updating configuration: {str(e)}")
            raise

    async def _create_configuration(self, config_data: dict):
        """Create a new configuration"""
        try:
            # Add metadata
            config_data['created_at'] = datetime.now(timezone.utc).isoformat()

            # If this config is being set as active, handle activation logic
            if config_data.get('is_active'):
                await self._handle_config_activation(
                    config_data['id'],
                    config_data['key']
                )

            return await self.db_service.save_configuration(config_data)
        except Exception as e:
            self.logger.error(f"Error creating configuration: {str(e)}")
            raise

    async def _handle_config_activation(self, config_id: str, config_key: str):
        """
        Handle configuration activation logic
        For certain config types (like MODEL_CONFIG), only one should be active
        """
        try:
            # Get all configurations of the same type
            configs = await self.db_service.get_configurations(config_id)

            # Deactivate other configurations of the same type
            for config in configs:
                if config['key'] != config_key and config.get('is_active'):
                    config['is_active'] = False
                    config['updated_at'] = datetime.now(timezone.utc).isoformat()
                    await self.db_service.update_configuration(config)

            self.logger.info(f"Activated configuration {config_key} in group {config_id}")
        except Exception as e:
            self.logger.error(f"Error handling configuration activation: {str(e)}")
            raise

    async def get_active_model_config(self):
        """Get active model configuration"""
        try:
            configs = await self.db_service.get_configurations('MODEL_CONFIG')
            return next(
                (c for c in configs if c.get('is_active')),
                None
            )
        except Exception as e:
            self.logger.error(f"Error getting active model config: {str(e)}")
            raise

    async def get_inference_params(self):
        """Get inference parameters configuration"""
        try:
            return await self.db_service.get_configurations('INFERENCE_PARAMS')
        except Exception as e:
            self.logger.error(f"Error getting inference parameters: {str(e)}")
            raise
