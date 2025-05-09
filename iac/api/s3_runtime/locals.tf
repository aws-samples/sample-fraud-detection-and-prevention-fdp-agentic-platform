# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

locals {
  fdp_gid = (
    try(trimspace(var.fdp_gid), "") == "" ? (
      data.aws_region.this.name == element(keys(var.fdp_backend_bucket), 0)
      ? random_id.this.hex : data.terraform_remote_state.s3.0.outputs.fdp_gid
    ) : var.fdp_gid
  )
  region = (
    data.aws_region.this.name == element(keys(var.fdp_backend_bucket), 0)
    ? element(keys(var.fdp_backend_bucket), 1) : element(keys(var.fdp_backend_bucket), 0)
  )
}
