# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

data "terraform_remote_state" "app" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.region
    bucket = var.fdp_backend_bucket[data.aws_region.this.region]
    key    = format(var.fdp_backend_pattern, "service_catalog_app_registry")
  }
}

data "terraform_remote_state" "iam" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.region
    bucket = var.fdp_backend_bucket[data.aws_region.this.region]
    key    = format(var.fdp_backend_pattern, "iam_role_assume")
  }
}

data "terraform_remote_state" "codebuild" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.region
    bucket = var.fdp_backend_bucket[data.aws_region.this.region]
    key    = format(var.fdp_backend_pattern, "iam_role_codebuild")
  }
}
