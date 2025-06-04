# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

dependency "cognito" {
  config_path  = "../cognito_identity_pool"
  skip_outputs = true
}

dependency "auth" {
  config_path  = "../iam_role_cognito_auth"
  skip_outputs = true
}

dependency "unauth" {
  config_path  = "../iam_role_cognito_unauth"
  skip_outputs = true
}
