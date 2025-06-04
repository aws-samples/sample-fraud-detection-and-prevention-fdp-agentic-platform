# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

q = {
  name            = "fdp-api"
  description     = "FDP COGNITO CLIENT"
  access_token    = "minutes"
  id_token        = "minutes"
  refresh_token   = "days"
  generate_secret = true
  secret_name     = "fdp-client-api"
  callback_url    = "http://localhost:3000"

  access_token_validity = 480
  id_token_validity     = 480

  allowed_oauth_flows_enabled  = true
  supported_identity_providers = "COGNITO"
  allowed_oauth_flows          = "code"
  allowed_oauth_scopes         = <<EOF
    aws.cognito.signin.user.admin,openid,
    email,profile,fdp/read,fdp/write
  EOF
  explicit_auth_flows          = <<EOF
    ALLOW_REFRESH_TOKEN_AUTH,
    ALLOW_USER_SRP_AUTH,
    ALLOW_CUSTOM_AUTH
  EOF
}
