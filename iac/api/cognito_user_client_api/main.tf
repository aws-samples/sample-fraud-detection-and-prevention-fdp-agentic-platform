# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

resource "aws_cognito_user_pool_client" "this" {
  name         = format("%s-%s", var.q.name, local.fdp_gid)
  user_pool_id = data.terraform_remote_state.cognito.outputs.id

  allowed_oauth_flows_user_pool_client = var.q.allowed_oauth_flows_enabled
  allowed_oauth_flows                  = split(",", var.q.allowed_oauth_flows)
  allowed_oauth_scopes                 = split(",", replace(replace(var.q.allowed_oauth_scopes, " ", ""), "\n", ""))
  explicit_auth_flows                  = split(",", replace(replace(var.q.explicit_auth_flows, " ", ""), "\n", ""))
  supported_identity_providers         = split(",", var.q.supported_identity_providers)

  callback_urls   = coalesce(
    var.q.callback_url != null ? [var.q.callback_url] : null
  )
  logout_urls     = coalesce(
    var.q.callback_url != null ? ["${var.q.callback_url}/signout"] : null
  )

  # read_attributes  = local.attributes
  # write_attributes = slice(local.attributes, 0, length(local.attributes) - 2)

  enable_token_revocation       = true
  prevent_user_existence_errors = "ENABLED"

  generate_secret        = var.q.generate_secret
  access_token_validity  = var.q.access_token_validity
  id_token_validity      = var.q.id_token_validity
  refresh_token_validity = var.q.refresh_token_validity

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

  name        = format("%s-%s-%s", var.q.secret_name, data.aws_region.this.region, local.fdp_gid)
  description = var.q.description

  force_overwrite_replica_secret = true
  recovery_window_in_days        = 0

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
    FDP_TFVAR_API_CLIENT_ID     = aws_cognito_user_pool_client.this.id
    FDP_TFVAR_API_CLIENT_SECRET = aws_cognito_user_pool_client.this.client_secret
  })
}
