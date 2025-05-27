# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Pre-Token Generator"""

import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def handler(event, context):
    """Main handler function for Lambda"""
    LOGGER.info("Received event: %s", json.dumps(event))

    # this allows us to override claims in the access token
    # "claimsAndScopeOverrideDetails" is the important part
    event["response"]["claimsAndScopeOverrideDetails"] = {
        "accessTokenGeneration": {
            "scopesToAdd": ["fdp/read", "fdp/write"]
        }
    }

    # return modified token to Cognito
    return event

if __name__ == '__main__':
    handler(event=None, context=None)
