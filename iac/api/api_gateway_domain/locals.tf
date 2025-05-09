# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

locals {
  domains = (
    try(trimspace(var.fdp_custom_domain), "") == "" ? {} : {
      global                                   = format(data.terraform_remote_state.cognito.outputs.global_pattern, var.fdp_custom_domain)
      element(keys(var.fdp_backend_bucket), 0) = format(data.terraform_remote_state.cognito.outputs.api_pattern, element(keys(var.fdp_backend_bucket), 0), var.fdp_custom_domain)
      element(keys(var.fdp_backend_bucket), 1) = format(data.terraform_remote_state.cognito.outputs.api_pattern, element(keys(var.fdp_backend_bucket), 1), var.fdp_custom_domain)
    }
  )
}
