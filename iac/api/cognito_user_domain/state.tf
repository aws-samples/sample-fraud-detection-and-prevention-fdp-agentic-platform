# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

output "aws_account_id" {
  value = aws_cognito_user_pool_domain.this.aws_account_id
}

output "cloudfront_distribution" {
  value = aws_cognito_user_pool_domain.this.cloudfront_distribution
}

output "cloudfront_distribution_arn" {
  value = aws_cognito_user_pool_domain.this.cloudfront_distribution_arn
}

output "cloudfront_distribution_zone_id" {
  value = aws_cognito_user_pool_domain.this.cloudfront_distribution_zone_id
}

output "s3_bucket" {
  value = aws_cognito_user_pool_domain.this.s3_bucket
}

output "version" {
  value = aws_cognito_user_pool_domain.this.version
}

output "auth_pattern" {
  value = var.q.auth_pattern
}

output "api_pattern" {
  value = var.q.api_pattern
}

output "global_pattern" {
  value = var.q.global_pattern
}

output "auth_url" {
  value = (
    aws_cognito_user_pool_domain.this.domain != data.terraform_remote_state.cognito.outputs.name
    ? format("https://%s", aws_cognito_user_pool_domain.this.domain)
    : format("https://%s.auth.%s.amazoncognito.com", aws_cognito_user_pool_domain.this.domain, data.aws_region.this.name)
  )
}

output "api_url" {
  value = (
    try(trimspace(var.fdp_custom_domain), "") == ""
    ? "" : format(format("https://%s", var.q.api_pattern), data.aws_region.this.name, var.fdp_custom_domain)
  )
}
