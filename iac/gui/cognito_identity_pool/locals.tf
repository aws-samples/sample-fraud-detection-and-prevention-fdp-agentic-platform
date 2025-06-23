# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

locals {
  fdp_gid = (
    try(trimspace(var.fdp_gid), "") == ""
    ? data.terraform_remote_state.s3.outputs.fdp_gid : var.fdp_gid
  )
  replicas = (
    data.terraform_remote_state.s3.outputs.region2 == data.aws_region.this.region
    ? [] : [data.terraform_remote_state.s3.outputs.region2]
  )
}
