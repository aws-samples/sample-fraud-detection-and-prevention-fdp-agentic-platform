# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

locals {
  fdp_gid = (
    try(trimspace(var.fdp_gid), "") == ""
    ? data.terraform_remote_state.iam.outputs.fdp_gid
    : var.fdp_gid
  )
  environment_variables = [
    {
      name  = "AWS_DEFAULT_REGION"
      type  = "PLAINTEXT"
      value = data.aws_region.this.name
    },
    {
      name  = "AWS_REGION"
      type  = "PLAINTEXT"
      value = data.aws_region.this.name
    },
    {
      name  = "FDP_REGION"
      type  = "PLAINTEXT"
      value = data.aws_region.this.name
    },
    {
      name  = "FDP_DIR"
      type  = "PLAINTEXT"
      value = "iac/api"
    },
    {
      name  = "FDP_GID"
      type  = "PLAINTEXT"
      value = local.fdp_gid
    },
    {
      name  = "FDP_BUCKET"
      type  = "PLAINTEXT"
      value = var.fdp_backend_bucket[data.aws_region.this.name]
    },
    {
      name  = "FDP_TFVAR_BACKEND_BUCKET"
      type  = "PLAINTEXT"
      value = format("{%s}", join(",", [for key, value in var.fdp_backend_bucket : "\"${key}\"=\"${value}\""]))
    },
    {
      name  = "FDP_TFVAR_ACCOUNT"
      type  = "PLAINTEXT"
      value = data.aws_caller_identity.this.account_id
    },
    {
      name  = "FDP_TFVAR_APP_ARN"
      type  = "PLAINTEXT"
      value = try(trimspace(var.fdp_app_arn), "") != "" ? var.fdp_app_arn : data.terraform_remote_state.app.outputs.arn
    },
    {
      name  = "FDP_TFVAR_VPC_ID"
      type  = "PLAINTEXT"
      value = ""
    },
    {
      name  = "FDP_TFVAR_VPCE_MAPPING"
      type  = "PLAINTEXT"
      value = ""
    },
    {
      name  = "FDP_TFVAR_SUBNETS_IGW_CREATE"
      type  = "PLAINTEXT"
      value = "false"
    },
    {
      name  = "FDP_TFVAR_SUBNETS_NAT_CREATE"
      type  = "PLAINTEXT"
      value = "false"
    },
    {
      name  = "FDP_TFVAR_SUBNETS_IGW_MAPPING"
      type  = "PLAINTEXT"
      value = ""
    },
    {
      name  = "FDP_TFVAR_SUBNETS_NAT_MAPPING"
      type  = "PLAINTEXT"
      value = ""
    },
  ]
}
