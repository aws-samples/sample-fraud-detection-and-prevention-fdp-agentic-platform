# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

resource "aws_s3_bucket" "this" {
  #checkov:skip=CKV_AWS_18:This solution does not require access logging for S3 based health checks (false positive)
  #checkov:skip=CKV_AWS_21:This solution does not require versioning for S3 based health checks (false positive)
  #checkov:skip=CKV_AWS_144:This solution does not require cross region replication for S3 based health checks (false positive)
  #checkov:skip=CKV_AWS_145:This solution does not require encryption for S3 based health checks (false positive)
  #checkov:skip=CKV2_AWS_6:This solution does require public access for S3 based health checks (false positive)
  #checkov:skip=CKV2_AWS_61:This solution does not require lifecycle for S3 based health checks (false positive)
  #checkov:skip=CKV2_AWS_62:This solution does not events notification lifecycle for S3 based health checks (false positive)

  bucket        = format("%s-%s-%s", var.q.bucket, data.aws_region.this.name, local.fdp_gid)
  force_destroy = var.q.force_destroy

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_s3_bucket_ownership_controls" "this" {
  bucket = aws_s3_bucket.this.id

  rule {
    object_ownership = var.q.object_ownership
  }
}

resource "aws_s3_bucket_acl" "this" {
  bucket = aws_s3_bucket.this.id
  acl    = "private"

  depends_on = [aws_s3_bucket_ownership_controls.this]
}

resource "aws_s3_bucket_logging" "this" {
  bucket        = aws_s3_bucket.this.id
  target_bucket = var.fdp_backend_bucket[data.aws_region.this.name]
  target_prefix = var.q.logs_prefix
}

resource "aws_s3_bucket_website_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  index_document {
    suffix = var.q.index_document
  }

  error_document {
    key = var.q.error_document
  }
}
