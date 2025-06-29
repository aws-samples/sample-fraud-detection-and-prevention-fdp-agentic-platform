# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

data "terraform_remote_state" "cognito" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.region
    bucket = var.fdp_backend_bucket[data.aws_region.this.region]
    key    = format(var.fdp_backend_pattern, "cognito_user_domain")
  }
}

data "terraform_remote_state" "dynamodb" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.region
    bucket = var.fdp_backend_bucket[data.aws_region.this.region]
    key    = format(var.fdp_backend_pattern, "dynamodb_tables")
  }
}

data "terraform_remote_state" "s3" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.region
    bucket = var.fdp_backend_bucket[data.aws_region.this.region]
    key    = format(var.fdp_backend_pattern, "s3_runtime")
  }
}

data "terraform_remote_state" "sgr" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.region
    bucket = var.fdp_backend_bucket[data.aws_region.this.region]
    key    = format(var.fdp_backend_pattern, "security_group")
  }
}

data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.region
    bucket = var.fdp_backend_bucket[data.aws_region.this.region]
    key    = format(var.fdp_backend_pattern, "vpc_subnet")
  }
}

data "aws_iam_policy_document" "this" {
  statement {
    effect  = "Allow"
    actions = [
      "dynamodb:CreateTable",
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:Scan",
      "dynamodb:Query",
      "dynamodb:BatchWriteItem",
    ]
    resources = [
      lookup(data.terraform_remote_state.dynamodb.outputs.arn, "agent", null),
      lookup(data.terraform_remote_state.dynamodb.outputs.arn, "config", null),
      lookup(data.terraform_remote_state.dynamodb.outputs.arn, "prompt", null),
      lookup(data.terraform_remote_state.dynamodb.outputs.arn, "strands", null),
      lookup(data.terraform_remote_state.dynamodb.outputs.arn, "agent2", null),
    ]
  }

  statement {
    effect  = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket",
      "s3:CreateBucket",
      "s3:HeadBucket",
      "s3:PutBucketEncryption",
      "s3:PutBucketVersioning",
    ]
    resources = [
      data.terraform_remote_state.s3.outputs.arn,
      "${data.terraform_remote_state.s3.outputs.arn}/*",
    ]
  }

  statement {
    effect  = "Allow"
    actions = [
      "bedrock:InvokeModel",
      "bedrock-runtime:InvokeModelWithResponseStream",
    ]
    resources = [
      format("arn:%s:bedrock:%s::foundation-model/*", data.aws_partition.this.id, "us-east-1"),
      format("arn:%s:bedrock:%s::foundation-model/*", data.aws_partition.this.id, data.aws_region.this.region),
    ]
  }
}
