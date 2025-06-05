# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# lib/models.py
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from decimal import Decimal
from enum import Enum

class DocumentAnalysisRequest(BaseModel):
    image_base64: str
    model_type: str = 'LITE'

class DocumentAnalysisResponse(BaseModel):
    pk: str
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
    pk: Optional[str] = None
    role: str
    tasks: str
    is_active: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class Configuration(BaseModel):
    pk: str
    sk: str
    value: str
    description: Optional[str] = None
    is_active: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# Strands Agent models
class VerificationStatus(str, Enum):
    """Verification status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    NEEDS_INFO = "needs_info"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentRequest(BaseModel):
    """Request model for starting a verification"""
    image_base64: str = Field(..., description="Base64 encoded image of the document")
    document_type: Optional[str] = Field(None, description="Type of document (if known)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class VerificationStep(BaseModel):
    """Model for a verification step"""
    step_id: str
    name: str
    description: str
    status: str
    confidence: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: str

class VerificationResult(BaseModel):
    """Model for verification result"""
    verification_id: str
    status: VerificationStatus
    document_type: Optional[str] = None
    confidence: Optional[float] = None
    steps: List[VerificationStep]
    needs_info: Optional[Dict[str, Any]] = None
    result_summary: Optional[str] = None
    file_key: Optional[str] = None
    preview_url: Optional[str] = None
    created_at: str
    updated_at: str
