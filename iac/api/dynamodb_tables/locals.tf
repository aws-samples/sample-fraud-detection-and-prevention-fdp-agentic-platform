# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

locals {
  fdp_gid = (
    try(trimspace(var.fdp_gid), "") == ""
    ? data.terraform_remote_state.s3.outputs.fdp_gid : var.fdp_gid
  )
  replicas = (
    data.aws_region.this.name != data.terraform_remote_state.s3.outputs.region2
    && data.aws_region.this.name == element(keys(var.fdp_backend_bucket), 0)
    ? [data.terraform_remote_state.s3.outputs.region2] : []
  )
  attributes = [
    {
      name = "pk"
      type = "S"
    },
    # {
    #   name = "sk"
    #   type = "S"
    # },
  ]
}
