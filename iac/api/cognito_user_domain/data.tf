# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

provider "aws" {
  alias  = "glob"
  region = "us-east-1"

  skip_region_validation = true
}

data "terraform_remote_state" "cognito" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.name
    bucket = var.fdp_backend_bucket[data.aws_region.this.name]
    key    = format(var.fdp_backend_pattern, "cognito_user_pool")
  }
}

data "aws_acm_certificate" "this" {
  provider = aws.glob
  count    = try(trimspace(var.fdp_custom_domain), "") == "" ? 0 : 1
  domain   = var.fdp_custom_domain
  statuses = ["ISSUED"]
}
