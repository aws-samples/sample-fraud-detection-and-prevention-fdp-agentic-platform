# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

output "arn" {
  value = aws_s3_bucket.this.arn
}

output "id" {
  value = aws_s3_bucket.this.id
}

output "bucket_domain_name" {
  value = aws_s3_bucket.this.bucket_domain_name
}

output "domain" {
  value = aws_s3_bucket.this.bucket_regional_domain_name
}

output "hosted_zone_id" {
  value = aws_s3_bucket.this.hosted_zone_id
}

output "prefix" {
  value = replace(replace(var.fdp_backend_pattern, "terraform/", "lambda/"), "terraform.tfstate", "function.zip")
}

output "role_name" {
  value = format("%s-%s-%s", var.q.assume_role_name, aws_s3_bucket.this.region, local.fdp_gid)
}

output "region" {
  value = aws_s3_bucket.this.region
}

output "region2" {
  value = local.region
}

output "fdp_gid" {
  value = local.fdp_gid
}
