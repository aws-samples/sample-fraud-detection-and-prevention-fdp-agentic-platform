# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

dependency "cognito" {
  config_path  = "../cognito_user_pool"
  skip_outputs = true
}

dependency "iam_logs" {
  config_path  = "../iam_role_agw_logs"
  skip_outputs = true
}

dependency "iam_sqs" {
  config_path  = "../iam_role_agw_sqs"
  skip_outputs = true
}

dependency "lambda" {
  config_path  = "../lambda_functions"
  skip_outputs = true
}

dependency "s3" {
  config_path  = "../s3_runtime"
  skip_outputs = true
}
