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

output "bucket_regional_domain_name" {
  value = aws_s3_bucket.this.bucket_regional_domain_name
}

output "bucket_logging" {
  value = data.terraform_remote_state.s3.outputs.bucket_domain_name
  # value = format("%s.s3.amazonaws.com", var.fdp_backend_bucket[data.aws_region.this.name])
}

output "hosted_zone_id" {
  value = aws_s3_bucket.this.hosted_zone_id
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

output "index_document" {
  value = var.q.index_document
}

output "error_document" {
  value = var.q.error_document
}
