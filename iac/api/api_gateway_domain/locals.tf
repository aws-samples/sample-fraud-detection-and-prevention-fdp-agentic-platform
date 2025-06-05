# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

locals {
  fdp_gid = (
    try(trimspace(var.fdp_gid), "") == ""
    ? data.terraform_remote_state.s3.outputs.fdp_gid : var.fdp_gid
  )
  replicas = (
    data.terraform_remote_state.s3.outputs.region2 == data.aws_region.this.name
    ? [] : [data.terraform_remote_state.s3.outputs.region2]
  )
  domains = (
    try(trimspace(var.fdp_custom_domain), "") == "" ? {} : {
      global                                   = format(data.terraform_remote_state.domain.outputs.global_pattern, var.fdp_custom_domain)
      element(keys(var.fdp_backend_bucket), 0) = format(data.terraform_remote_state.domain.outputs.api_pattern, element(keys(var.fdp_backend_bucket), 0), var.fdp_custom_domain)
      element(keys(var.fdp_backend_bucket), 1) = format(data.terraform_remote_state.domain.outputs.api_pattern, element(keys(var.fdp_backend_bucket), 1), var.fdp_custom_domain)
    }
  )
}
