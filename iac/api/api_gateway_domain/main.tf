# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

resource "aws_api_gateway_domain_name" "this" {
  #checkov:skip=CKV_AWS_206:This solution leverages TLS_1_2 security policy (false positive)

  for_each                 = local.domains
  domain_name              = each.value
  regional_certificate_arn = element(data.aws_acm_certificate.this.*.arn, 0)
  security_policy          = var.q.security_policy

  endpoint_configuration {
    types = var.types
  }
}

resource "aws_api_gateway_base_path_mapping" "healthy" {
  for_each    = local.domains
  domain_name = each.value
  api_id      = data.terraform_remote_state.agw_rest.outputs.id
  stage_name  = data.terraform_remote_state.agw_rest.outputs.stage_name
  base_path   = var.q.base_path_healthy
}

resource "aws_api_gateway_base_path_mapping" "unhealthy" {
  for_each    = local.domains
  domain_name = each.value
  api_id      = data.terraform_remote_state.agw_mock.outputs.id
  stage_name  = data.terraform_remote_state.agw_mock.outputs.stage_name
  base_path   = var.q.base_path_unhealthy
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
    FDP_TFVAR_API_GATEWAY_URL = (
      data.terraform_remote_state.domain.outputs.api_url != ""
      ? data.terraform_remote_state.domain.outputs.api_url
      : data.terraform_remote_state.agw_rest.outputs.stage_invoke_url
    )
    FDP_TFVAR_COGNITO_AUTH_URL      = data.terraform_remote_state.domain.outputs.auth_url
    FDP_TFVAR_COGNITO_IDP_URL       = format("https://%s", data.terraform_remote_state.cognito.outputs.endpoint)
    FDP_TFVAR_COGNITO_USER_POOL_ID  = data.terraform_remote_state.cognito.outputs.id
    FDP_TFVAR_COGNITO_API_CLIENT_ID = data.terraform_remote_state.client.outputs.client_id
    FDP_TFVAR_REGION                = data.aws_region.this.region
  })
}
