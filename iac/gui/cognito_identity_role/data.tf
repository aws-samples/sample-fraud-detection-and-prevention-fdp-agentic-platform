# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

data "terraform_remote_state" "cognito" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.name
    bucket = var.fdp_backend_bucket[data.aws_region.this.name]
    key    = format(var.fdp_backend_pattern, "cognito_identity_pool")
  }
}

data "terraform_remote_state" "auth" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.name
    bucket = var.fdp_backend_bucket[data.aws_region.this.name]
    key    = format(var.fdp_backend_pattern, "iam_role_cognito_auth")
  }
}

data "terraform_remote_state" "unauth" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.name
    bucket = var.fdp_backend_bucket[data.aws_region.this.name]
    key    = format(var.fdp_backend_pattern, "iam_role_cognito_unauth")
  }
}
