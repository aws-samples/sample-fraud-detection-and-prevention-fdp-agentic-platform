# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

output "arn" {
  value = { for k, v in aws_api_gateway_domain_name.this : k => v.arn }
}

output "id" {
  value = { for k, v in aws_api_gateway_domain_name.this : k => v.id }
}

output "regional_zone_id" {
  value = { for k, v in aws_api_gateway_domain_name.this : k => v.regional_zone_id }
}

output "regional_domain_name" {
  value = { for k, v in aws_api_gateway_domain_name.this : k => v.regional_domain_name }
}

output "certificate_upload_date" {
  value = { for k, v in aws_api_gateway_domain_name.this : k => v.certificate_upload_date }
}

output "cloudfront_zone_id" {
  value = { for k, v in aws_api_gateway_domain_name.this : k => v.cloudfront_zone_id }
}

output "cloudfront_domain_name" {
  value = { for k, v in aws_api_gateway_domain_name.this : k => v.cloudfront_domain_name }
}

output "stage_invoke_url" {
  value = data.terraform_remote_state.agw_rest.outputs.stage_invoke_url
}
