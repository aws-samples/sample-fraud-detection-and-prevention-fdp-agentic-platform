# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

locals {
  fdp_gid = (
    try(trimspace(var.fdp_gid), "") == ""
    ? data.terraform_remote_state.s3.outputs.fdp_gid : var.fdp_gid
  )
  env_vars = {
    FDP_LOGGING         = var.q.logging
    FDP_ID              = local.fdp_gid
    FDP_ACCOUNT         = data.aws_caller_identity.this.account_id
    FDP_REGION          = data.aws_region.this.name
    FDP_CHECK_REGION    = data.terraform_remote_state.s3.outputs.region2
    FDP_API_URL         = data.terraform_remote_state.cognito.outputs.api_url
    FDP_AUTH_URL        = data.terraform_remote_state.cognito.outputs.auth_url
    FDP_DDB_AGENT       = lookup(data.terraform_remote_state.dynamodb.outputs.id, "agent", null)
    FDP_DDB_CONFIG      = lookup(data.terraform_remote_state.dynamodb.outputs.id, "config", null)
    FDP_DDB_PROMPT      = lookup(data.terraform_remote_state.dynamodb.outputs.id, "prompt", null)
    FDP_S3_BUCKET       = data.terraform_remote_state.s3.outputs.id
    SECRETS_MANAGER_TTL = var.q.secrets_manager_ttl
  }
  iam_policies_arns = [
    "arn:${data.aws_partition.this.partition}:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
    # "arn:${data.aws_partition.this.partition}:iam::aws:policy/AmazonS3ReadOnlyAccess",
    # "arn:${data.aws_partition.this.partition}:iam::aws:policy/AmazonDynamoDBReadOnlyAccess",
  ]
}
