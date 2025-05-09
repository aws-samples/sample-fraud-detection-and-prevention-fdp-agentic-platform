# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# lib/models.py
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class DocumentAnalysisRequest(BaseModel):
    image_base64: str
    model_type: str = 'LITE'

class DocumentAnalysisResponse(BaseModel):
    id: str
    timestamp: str
    document_type: str
    confidence: float
    content_text: str
    file_key: Optional[str] = None
    preview_url: Optional[str] = None

    class Config:
        json_encoders = {
            Decimal: float
        }
        arbitrary_types_allowed = True

class Prompt(BaseModel):
    id: Optional[str] = None
    role: str
    tasks: str
    is_active: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class Configuration(BaseModel):
    id: str
    key: str
    value: str
    description: Optional[str] = None
    is_active: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
