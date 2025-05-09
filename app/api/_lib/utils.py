# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# lib/utils.py
import re
import logging

logger = logging.getLogger(__name__)

def extract_confidence_score(text: str) -> float:
    try:
        # First try to find the exact pattern
        pattern = r'\*{0,2}Confidence Score:\*{0,2}\s*(\d+(?:\.\d+)?)'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            value = float(match.group(1))
            return value / 100 if value > 1 else value
            
        patterns = [
            r'\*{0,2}confidence:?\*{0,2}\s*(\d+(?:\.\d+)?)',
            r'\*{0,2}confidence level:?\*{0,2}\s*(\d+(?:\.\d+)?)',
            r'\*{0,2}confidence rating:?\*{0,2}\s*(\d+(?:\.\d+)?)',
            r'\*{0,2}Confidence Score for Check Authenticity:?\*{0,2}\s*(\d+(?:\.\d+)?)',
            r'\*{0,2}Confidence Score for Document Authenticity:?\*{0,2}\s*(\d+(?:\.\d+)?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                return value / 100 if value > 1 else value
        
        return 0.0
        
    except Exception as e:
        logger.error(f"Error extracting confidence score: {str(e)}")
        return 0.0

def extract_document_type(text: str) -> str:
    try:
        pattern = r'\*{0,2}Document Type:\*{0,2}\s*([^\n]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(1).strip().replace('*', '')
            
        patterns = [
            r'\*{0,2}type of document:?\*{0,2}\s*([^\n]+)',
            r'\*{0,2}document:?\*{0,2}\s*([^\n]+)',
            r'\*{0,2}identified as:?\*{0,2}\s*([^\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip().replace('*', '')
        
        return "Unknown Document"
        
    except Exception as e:
        logger.error(f"Error extracting document type: {str(e)}")
        return "Unknown Document"

def create_api_response(status_code: int, body: dict) -> dict:
    """Create standardized API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        },
        'body': json.dumps(body)
    }
