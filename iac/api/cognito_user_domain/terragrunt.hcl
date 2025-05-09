# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

dependency "cognito" {
  config_path  = "../cognito_user_pool"
  skip_outputs = true
}
