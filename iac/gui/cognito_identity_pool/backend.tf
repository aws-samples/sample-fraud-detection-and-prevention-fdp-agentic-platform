# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

terraform {
  backend "s3" {
    use_lockfile           = true
    skip_region_validation = true

    key = "terraform/github/fdp/cognito_identity_pool/terraform.tfstate"
  }
}
