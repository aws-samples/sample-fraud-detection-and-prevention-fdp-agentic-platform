# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

locals {
  fdp_gid = (
    try(trimspace(var.fdp_gid), "") == ""
    ? data.terraform_remote_state.iam.outputs.fdp_gid
    : var.fdp_gid
  )
  statements = [
    {
      actions = "codebuild:CreateReportGroup,codebuild:CreateReport,codebuild:UpdateReport,codebuild:BatchPutTestCases,codebuild:BatchPutCodeCoverages"
      resources = format(
        "arn:%s:codebuild:*:%s:report-group/fdp-*",
        data.aws_partition.this.partition,
        data.aws_caller_identity.this.account_id
      )
    },
    {
      actions = "logs:CreateLogGroup,logs:CreateLogStream,logs:PutLogEvents"
      resources = format(
        "arn:%s:logs:*:%s:log-group:/aws/codebuild/fdp-*",
        data.aws_partition.this.partition,
        data.aws_caller_identity.this.account_id
      )
    },
    {
      actions = "s3:GetBucket*,s3:ListBucket*"
      resources = format(
        "arn:%s:s3:::%s",
        data.aws_partition.this.partition,
        var.fdp_backend_bucket[data.aws_region.this.region]
      )
    },
    {
      actions = "s3:GetObject*,s3:PutObject*"
      resources = format(
        "arn:%s:s3:::%s/*",
        data.aws_partition.this.partition,
        var.fdp_backend_bucket[data.aws_region.this.region]
      )
    },
  ]
}
