# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

module "lambda" {
  count         = length(var.r)
  source        = "terraform-aws-modules/lambda/aws"
  version       = "~> 7.0"
  function_name = format("%s-%s", var.r[count.index]["name"], local.fdp_gid)
  description   = var.r[count.index]["desc"]
  package_type  = var.q.package_type
  architectures = [var.q.architecture]
  handler       = var.q.handler
  runtime       = var.q.runtime
  memory_size   = var.q.memory_size
  timeout       = var.q.timeout
  tracing_mode  = var.q.tracing_mode
  store_on_s3   = true
  s3_bucket     = var.fdp_backend_bucket[data.aws_region.this.region]
  s3_prefix     = format(data.terraform_remote_state.s3.outputs.prefix, var.r[count.index]["name"])

  source_path = {
    path             = var.r[count.index]["path"]
    pip_requirements = format("%s/%s", var.r[count.index]["path"], var.r[count.index]["file"])
    pip_tmp_dir      = "/tmp"
    patterns         = ["!venv/.*"]
  }

  create_role        = true
  role_name          = format("%s-role-%s-%s", var.r[count.index]["name"], data.aws_region.this.region, local.fdp_gid)
  role_path          = "/service-role/"
  policy_path        = "/service-role/"
  attach_policies    = true
  number_of_policies = length(local.iam_policies_arns)
  policies           = local.iam_policies_arns
  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.this.json

  attach_cloudwatch_logs_policy     = true
  attach_dead_letter_policy         = true
  use_existing_cloudwatch_log_group = var.q.log_group_exists
  cloudwatch_logs_retention_in_days = var.q.retention_in_days
  cloudwatch_logs_skip_destroy      = var.q.skip_destroy
  dead_letter_target_arn            = element(aws_sqs_queue.this.*.arn, count.index)
  ephemeral_storage_size            = var.q.storage_size

  environment_variables = {
    for key, value in local.env_vars :
    key => value if try(trimspace(value), "") != ""
  }
  vpc_security_group_ids = (
    var.q.public == null
    ? null : [data.terraform_remote_state.sgr.outputs.id]
  )
  vpc_subnet_ids = (
    var.q.public == null
    ? null : var.q.public == true
    ? data.terraform_remote_state.vpc.outputs.igw_subnet_ids
    : data.terraform_remote_state.vpc.outputs.nat_subnet_ids
  )
}

resource "aws_sqs_queue" "this" {
  #checkov:skip=CKV_AWS_27:This solution leverages KMS encryption using AWS managed keys instead of CMKs (false positive)

  count                   = length(var.r)
  name                    = format("%s-lambda-dlq-%s", var.r[count.index]["name"], local.fdp_gid)
  sqs_managed_sse_enabled = var.q.sqs_managed_sse_enabled
}
