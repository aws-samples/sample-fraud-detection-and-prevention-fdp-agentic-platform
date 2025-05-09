# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

resource "aws_cognito_identity_pool_roles_attachment" "this" {
  identity_pool_id = data.terraform_remote_state.cognito.outputs.id

  roles = {
    "authenticated"   = data.terraform_remote_state.auth.outputs.arn
    "unauthenticated" = data.terraform_remote_state.unauth.outputs.arn
  }
}
