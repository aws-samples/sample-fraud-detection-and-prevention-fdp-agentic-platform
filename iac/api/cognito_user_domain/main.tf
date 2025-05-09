# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

resource "aws_cognito_user_pool_domain" "this" {
  user_pool_id = data.terraform_remote_state.cognito.outputs.id
  domain = (
    try(trimspace(var.fdp_custom_domain), "") == ""
    ? data.terraform_remote_state.cognito.outputs.name
    : format(var.q.auth_pattern, data.aws_region.this.name, var.fdp_custom_domain)
  )
  certificate_arn = (
    try(trimspace(var.fdp_custom_domain), "") == ""
    ? null : element(data.aws_acm_certificate.this.*.arn, 0)
  )
}
