# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

output "arn" {
  value = aws_cloudfront_distribution.this.arn
}

output "id" {
  value = aws_cloudfront_distribution.this.id
}

output "caller_reference" {
  value = aws_cloudfront_distribution.this.caller_reference
}

output "domain_name" {
  value = aws_cloudfront_distribution.this.domain_name
}

output "hosted_zone_id" {
  value = aws_cloudfront_distribution.this.hosted_zone_id
}

output "last_modified_time" {
  value = aws_cloudfront_distribution.this.last_modified_time
}

output "status" {
  value = aws_cloudfront_distribution.this.status
}
