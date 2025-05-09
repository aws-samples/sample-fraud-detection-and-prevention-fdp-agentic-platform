# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

data "aws_service_principal" "this" {
  service_name = "cognito-identity"
  region       = data.aws_region.this.name
}

data "aws_iam_policy_document" "this" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [data.aws_service_principal.this.name]
    }

    condition {
      test     = "ForAnyValue:StringLike"
      variable = format("%s:amr", data.aws_service_principal.this.name)
      values   = ["unauthenticated"]
    }

    condition {
      test     = "StringEquals"
      variable = format("%s:aud", data.aws_service_principal.this.name)
      values   = [data.terraform_remote_state.cognito.outputs.id]
    }
  }
}

data "terraform_remote_state" "cognito" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.name
    bucket = var.fdp_backend_bucket[data.aws_region.this.name]
    key    = format(var.fdp_backend_pattern, "cognito_identity_pool")
  }
}

data "terraform_remote_state" "s3" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.name
    bucket = var.fdp_backend_bucket[data.aws_region.this.name]
    key    = format(var.fdp_backend_pattern, "s3_runtime")
  }
}
