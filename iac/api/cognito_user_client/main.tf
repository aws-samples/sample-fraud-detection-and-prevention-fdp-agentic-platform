# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

resource "aws_cognito_user_pool_client" "api" {
  name         = format("%s-%s", var.q.name_api, local.fdp_gid)
  user_pool_id = data.terraform_remote_state.cognito.outputs.id

  allowed_oauth_flows_user_pool_client = var.q.allowed_oauth_flows_user_pool_client
  allowed_oauth_flows                  = var.allowed_oauth_flows
  allowed_oauth_scopes                 = var.allowed_oauth_scopes
  supported_identity_providers         = var.supported_identity_providers
  # explicit_auth_flows                  = var.explicit_auth_flows
  generate_secret                      = null # true

  # read_attributes  = local.attributes
  # write_attributes = slice(local.attributes, 0, length(local.attributes) - 2)

  access_token_validity = var.q.access_token_validity
  id_token_validity     = var.q.id_token_validity

  token_validity_units {
    access_token  = var.q.access_token
    id_token      = var.q.id_token
    refresh_token = var.q.refresh_token
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_cognito_user_pool_client" "web" {
  name         = format("%s-%s", var.q.name_web, local.fdp_gid)
  user_pool_id = data.terraform_remote_state.cognito.outputs.id

  allowed_oauth_flows_user_pool_client = var.q.allowed_oauth_flows_user_pool_client
  allowed_oauth_flows                  = var.allowed_oauth_flows
  allowed_oauth_scopes                 = var.allowed_oauth_scopes
  supported_identity_providers         = var.supported_identity_providers
  # explicit_auth_flows                  = var.explicit_auth_flows
  generate_secret                      = null # true

  # read_attributes  = local.attributes
  # write_attributes = slice(local.attributes, 0, length(local.attributes) - 2)

  access_token_validity = var.q.access_token_validity
  id_token_validity     = var.q.id_token_validity

  token_validity_units {
    access_token  = var.q.access_token
    id_token      = var.q.id_token
    refresh_token = var.q.refresh_token
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_secretsmanager_secret" "this" {
  #checkov:skip=CKV_AWS_149:This solution leverages KMS encryption using AWS managed keys instead of CMKs (false positive)
  #checkov:skip=CKV2_AWS_57:This solution does not require key automatic rotation -- managed by AWS (false positive)

  name        = format("%s-%s-%s", var.q.secret_name, data.aws_region.this.name, local.fdp_gid)
  description = var.q.description

  force_overwrite_replica_secret = true

  dynamic "replica" {
    for_each = local.replicas
    content {
      region = replica.value
    }
  }
}

resource "aws_secretsmanager_secret_version" "this" {
  secret_id = aws_secretsmanager_secret.this.id
  secret_string = jsonencode({
    FDP_API_CLIENT_ID     = aws_cognito_user_pool_client.api.id
    FDP_API_CLIENT_SECRET = aws_cognito_user_pool_client.api.client_secret
    FDP_WEB_CLIENT_ID     = aws_cognito_user_pool_client.web.id
    FDP_WEB_CLIENT_SECRET = aws_cognito_user_pool_client.web.client_secret
  })
}
