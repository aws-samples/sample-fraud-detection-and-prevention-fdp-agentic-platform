# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

dependency "auth" {
  config_path  = "../cognito_user_domain"
  skip_outputs = true
}

dependency "dynamodb" {
  config_path  = "../dynamodb_tables"
  skip_outputs = true
}

dependency "s3" {
  config_path  = "../s3_runtime"
  skip_outputs = true
}

dependency "sgr" {
  config_path  = "../security_group"
  skip_outputs = true
}

dependency "vpc" {
  config_path  = "../vpc_subnet"
  skip_outputs = true
}
