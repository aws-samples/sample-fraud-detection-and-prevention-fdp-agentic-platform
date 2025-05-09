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
