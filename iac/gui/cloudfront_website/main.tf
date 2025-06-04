# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

resource "aws_cloudfront_origin_access_control" "this" {
  name                              = local.s3_origin_id
  description                       = var.q.description
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "this" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = var.q.description
  default_root_object = data.terraform_remote_state.s3.outputs.index_document
  price_class         = "PriceClass_200"
  # web_acl_id          = data.terraform_remote_state.waf.outputs.arn

  # aliases = ["mysite.example.com", "yoursite.example.com"]

  origin {
    domain_name              = data.terraform_remote_state.s3.outputs.bucket_domain_name
    origin_id                = local.s3_origin_id
    origin_access_control_id = aws_cloudfront_origin_access_control.this.id
  }

  custom_error_response {
    error_code            = 404
    error_caching_min_ttl = 300
    response_code         = 200
    response_page_path    = format("/%s", data.terraform_remote_state.s3.outputs.index_document)
  }

  logging_config {
    include_cookies = false
    bucket          = data.terraform_remote_state.s3.outputs.bucket_logging
    prefix          = var.q.logs_prefix
  }

  default_cache_behavior {
    allowed_methods = ["GET", "HEAD", "OPTIONS", "DELETE", "PATCH", "POST", "PUT"]
    cached_methods  = ["GET", "HEAD"]

    default_ttl = var.q.default_ttl
    max_ttl     = var.q.max_ttl
    min_ttl     = var.q.min_ttl

    target_origin_id       = local.s3_origin_id
    viewer_protocol_policy = var.q.cache_viewer

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
      # restriction_type = "whitelist"
      # locations        = ["US", "CA", "GB", "DE"]
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

resource "aws_s3_bucket_policy" "this" {
  bucket = data.terraform_remote_state.s3.outputs.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontServicePrincipal"
        Effect    = "Allow"
        Principal = {
          Service = data.aws_service_principal.this.name
        }
        Action = "s3:GetObject"
        Resource = format("%s/*", data.terraform_remote_state.s3.outputs.arn)
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = format(
              "arn:aws:cloudfront::%s:distribution/%s",
              data.aws_caller_identity.this.account_id,
              aws_cloudfront_distribution.this.id
            )
          }
        }
      }
    ]
  })
}
