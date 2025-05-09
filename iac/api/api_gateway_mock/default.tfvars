# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

q = {
  name    = "fdp-agw-unhealthy"
  mode    = "overwrite"
  file    = "swagger.json.tftpl"
  version = "2023-01-30T23:30:40Z"
  stage   = "v0"
  format  = "$context.identity.sourceIp $context.identity.caller $context.identity.user [$context.requestTime] \"$context.httpMethod $context.resourcePath $context.protocol\" $context.status $context.responseLength $context.requestId"

  cw_group_name_prefix = "API-Gateway-Execution-Logs"
  retention_in_days    = 5
  skip_destroy         = true
}

types = ["REGIONAL"]
