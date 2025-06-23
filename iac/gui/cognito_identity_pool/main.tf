# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

resource "aws_cognito_identity_pool" "this" {
  identity_pool_name               = format("%s-%s-%s", var.q.name, data.aws_region.this.region, local.fdp_gid)
  allow_unauthenticated_identities = var.q.allow_unauthenticated_identities
  allow_classic_flow               = var.q.allow_classic_flow

  cognito_identity_providers {
    client_id               = data.terraform_remote_state.client.outputs.client_id
    provider_name           = replace(data.terraform_remote_state.client.outputs.user_pool_endpoint, "https://", "")
    server_side_token_check = var.q.server_side_token_check
  }

  cognito_identity_providers {
    client_id               = data.terraform_remote_state.client.outputs.api_client_id
    provider_name           = replace(data.terraform_remote_state.client.outputs.user_pool_endpoint, "https://", "")
    server_side_token_check = var.q.server_side_token_check
  }
}

resource "aws_secretsmanager_secret" "this" {
  #checkov:skip=CKV_AWS_149:This solution leverages KMS encryption using AWS managed keys instead of CMKs (false positive)
  #checkov:skip=CKV2_AWS_57:This solution does not require key automatic rotation -- managed by AWS (false positive)

  name        = format("%s-%s-%s", var.q.secret_name, data.aws_region.this.region, local.fdp_gid)
  description = var.q.description

  force_overwrite_replica_secret = var.q.force_overwrite
  recovery_window_in_days        = var.q.recovery_in_days

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
    FDP_TFVAR_COGNITO_IDENTITY_POOL_ID = aws_cognito_identity_pool.this.id
    FDP_TFVAR_COGNITO_WEB_CLIENT_ID    = data.terraform_remote_state.client.outputs.client_id
    FDP_TFVAR_CLOUDFRONT_ID            = data.terraform_remote_state.cloudfront.outputs.id
    FDP_TFVAR_CLOUDFRONT_URL           = format("https://%s", data.terraform_remote_state.cloudfront.outputs.domain_name)
    FDP_TFVAR_WEBSITE                  = data.terraform_remote_state.s3.outputs.id
    FDP_TFVAR_REGION                   = data.aws_region.this.region
  })
}
