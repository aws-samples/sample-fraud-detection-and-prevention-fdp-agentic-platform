# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Prompt Manager"""

# lib/prompt_manager.py
from datetime import datetime, timezone
import uuid

class PromptManager:
    """Prompt Manager"""
    def __init__(self, services, logger):
        self.db_service = services['db_service']
        self.logger = logger

    async def get_prompts(self):
        """Retrieve all prompts"""
        try:
            return await self.db_service.get_prompts()
        except Exception as e:
            self.logger.error("Error retrieving prompts: %s", str(e))
            raise

    async def create_prompt(self, prompt_data: dict):
        """Create a new prompt"""
        try:
            # Add metadata
            prompt_data['id'] = str(uuid.uuid4())
            prompt_data['created_at'] = datetime.now(timezone.utc).isoformat()

            # If this prompt is being set as active, deactivate others
            if prompt_data.get('is_active'):
                await self._deactivate_other_prompts()

            return await self.db_service.save_prompt(prompt_data)
        except Exception as e:
            self.logger.error("Error creating prompt: %s", str(e))
            raise

    async def update_prompt(self, prompt_id: str, prompt_data: dict):
        """Update an existing prompt"""
        try:
            # Verify prompt exists
            existing_prompt = await self.db_service.get_prompt(prompt_id)
            if not existing_prompt:
                raise ValueError(f"Prompt with id {prompt_id} not found")

            # Update metadata
            prompt_data['id'] = prompt_id
            prompt_data['updated_at'] = datetime.now(timezone.utc).isoformat()
            prompt_data['created_at'] = existing_prompt.get('created_at')

            # If this prompt is being set as active, deactivate others
            if prompt_data.get('is_active'):
                await self._deactivate_other_prompts(exclude_id=prompt_id)

            return await self.db_service.update_prompt(prompt_data)
        except Exception as e:
            self.logger.error("Error updating prompt: %s", str(e))
            raise

    async def delete_prompt(self, prompt_id: str):
        """Delete a prompt"""
        try:
            # Verify prompt exists
            existing_prompt = await self.db_service.get_prompt(prompt_id)
            if not existing_prompt:
                raise ValueError(f"Prompt with id {prompt_id} not found")

            # If this was the active prompt, we should probably warn about that
            if existing_prompt.get('is_active'):
                self.logger.warning(f"Deleting active prompt {prompt_id}")

            await self.db_service.delete_prompt(prompt_id)
        except Exception as e:
            self.logger.error("Error deleting prompt: %s", str(e))
            raise

    async def get_prompt(self, prompt_id: str):
        """Retrieve a specific prompt"""
        try:
            prompt = await self.db_service.get_prompt(prompt_id)
            if not prompt:
                raise ValueError(f"Prompt with id {prompt_id} not found")
            return prompt
        except Exception as e:
            self.logger.error("Error retrieving prompt: %s", str(e))
            raise

    async def _deactivate_other_prompts(self, exclude_id: str = None):
        """Helper method to deactivate all other prompts"""
        try:
            prompts = await self.db_service.get_prompts()
            for prompt in prompts:
                if prompt.get('is_active') and prompt.get('id') != exclude_id:
                    prompt['is_active'] = False
                    prompt['updated_at'] = datetime.now(timezone.utc).isoformat()
                    await self.db_service.update_prompt(prompt)
        except Exception as e:
            self.logger.error("Error deactivating prompts: %s", str(e))
            raise
