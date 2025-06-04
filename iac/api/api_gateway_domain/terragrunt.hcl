# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

dependency "agw_mock" {
  config_path  = "../api_gateway_mock"
  skip_outputs = true
}

dependency "agw_rest" {
  config_path  = "../api_gateway_rest"
  skip_outputs = true
}

dependency "cognito" {
  config_path  = "../cognito_user_pool"
  skip_outputs = true
}

dependency "domain" {
  config_path  = "../cognito_user_domain"
  skip_outputs = true
}

dependency "s3" {
  config_path  = "../s3_runtime"
  skip_outputs = true
}
