# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

resource "aws_api_gateway_rest_api" "this" {
  name              = format("%s-%s", var.q.name, local.fdp_gid)
  put_rest_api_mode = var.q.mode

  body = templatefile(var.q.file, {
    title       = format("%s-%s", var.q.name, local.fdp_gid)
    version     = var.q.version
    region      = data.aws_region.this.region
    cognito_key = format("%s-%s", var.q.name, local.fdp_gid)
    cognito_arn = data.terraform_remote_state.cognito.outputs.arn
    lambda_arn  = data.terraform_remote_state.lambda.outputs.invoke_arn
    failover_url = (
      data.terraform_remote_state.auth.outputs.api_url == "" ? "" : replace(
        data.terraform_remote_state.auth.outputs.api_url,
        data.terraform_remote_state.s3.outputs.region,
        data.terraform_remote_state.s3.outputs.region2
      )
    )
  })

  endpoint_configuration {
    types = var.types
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_deployment" "this" {
  rest_api_id = aws_api_gateway_rest_api.this.id

  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.this.body))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "this" {
  #checkov:skip=CKV_AWS_73:This solution does not require XRay in production (false positive)
  #checkov:skip=CKV_AWS_120:This solution does not require caching (false positive)
  #checkov:skip=CKV2_AWS_29:This solution does not require WAF yet (false positive)
  #checkov:skip=CKV2_AWS_51:This solution does not require client certs due to OAuth 2.0 implementation (false positive)

  deployment_id = aws_api_gateway_deployment.this.id
  rest_api_id   = aws_api_gateway_rest_api.this.id
  stage_name    = var.q.stage

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.this.arn
    format          = var.q.format
  }
}

resource "aws_api_gateway_method_settings" "this" {
  #checkov:skip=CKV_AWS_225:This solution does not require caching (false positive)
  #checkov:skip=CKV_AWS_308:This solution does not require caching (false positive)

  rest_api_id = aws_api_gateway_rest_api.this.id
  stage_name  = aws_api_gateway_stage.this.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled = true
    logging_level   = "ERROR"
  }
}

resource "aws_api_gateway_account" "this" {
  cloudwatch_role_arn = data.terraform_remote_state.iam_logs.outputs.arn
}

resource "aws_cloudwatch_log_group" "this" {
  #checkov:skip=CKV_AWS_158:This solution leverages CloudWatch logs (false positive)

  name              = format("%s_%s/%s", var.q.cw_group_name_prefix, aws_api_gateway_rest_api.this.id, var.q.stage)
  retention_in_days = var.q.retention_in_days
  skip_destroy      = var.q.skip_destroy
}

resource "aws_lambda_permission" "this" {
  count         = length(local.lambdas)
  action        = "lambda:InvokeFunction"
  principal     = data.aws_service_principal.this.name
  function_name = data.terraform_remote_state.lambda.outputs.name[local.lambdas[count.index]]
  source_arn    = format("%s/*/*", aws_api_gateway_rest_api.this.execution_arn)
}
