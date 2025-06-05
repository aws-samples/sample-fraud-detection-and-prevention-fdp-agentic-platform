# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

dependency "client" {
  config_path  = "../cognito_user_client_gui"
  skip_outputs = true
}

dependency "cloudfront" {
  config_path  = "../cloudfront_website"
  skip_outputs = true
}

dependency "s3" {
  config_path  = "../s3_website"
  skip_outputs = true
}
