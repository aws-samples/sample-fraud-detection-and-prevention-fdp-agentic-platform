# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

q = {
  name_api      = "fdp-api"
  name_web      = "fdp-web"
  description   = "FDP COGNITO CLIENT"
  access_token  = "minutes"
  id_token      = "minutes"
  refresh_token = "days"
  secret_name   = "fdp-client-api"

  access_token_validity = 480
  id_token_validity     = 480

  allowed_oauth_flows_user_pool_client = false # true
}

allowed_oauth_flows          = null # ["client_credentials"]
allowed_oauth_scopes         = null # ["fdp/read", "fdp/write"]
supported_identity_providers = null # ["COGNITO"]

explicit_auth_flows = [
  "ALLOW_ADMIN_USER_PASSWORD_AUTH",
  "ALLOW_CUSTOM_AUTH",
  "ALLOW_REFRESH_TOKEN_AUTH",
  "ALLOW_USER_PASSWORD_AUTH",
  "ALLOW_USER_SRP_AUTH"
]
