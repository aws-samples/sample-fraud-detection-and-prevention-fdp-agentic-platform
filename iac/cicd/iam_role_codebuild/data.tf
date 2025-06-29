# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

data "aws_service_principal" "this" {
  service_name = "codebuild"
  region       = data.aws_region.this.region
}

data "aws_iam_policy_document" "role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = [data.aws_service_principal.this.name]
    }
  }
}

data "aws_iam_policy_document" "policy" {
  #checkov:skip=CKV_AWS_109:This solution defines IAM policies have constrains with conditions in place (false positive)

  dynamic "statement" {
    for_each = local.statements
    content {
      effect    = "Allow"
      actions   = split(",", statement.value.actions)
      resources = split(",", statement.value.resources)
    }
  }

  statement {
    effect    = "Allow"
    actions   = ["sts:AssumeRole"]
    resources = [data.terraform_remote_state.iam.outputs.arn]

    condition {
      test     = "IpAddress"
      variable = "aws:SourceIp"
      values   = data.terraform_remote_state.iam.outputs.ips
    }

    condition {
      test     = "StringEquals"
      variable = "aws:ResourceAccount"
      values   = [data.aws_caller_identity.this.account_id]
    }
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
