# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

locals {
  region = (
    data.aws_region.this.region == element(keys(var.fdp_backend_bucket), 0)
    ? element(keys(var.fdp_backend_bucket), 1) : element(keys(var.fdp_backend_bucket), 0)
  )
  fdp_gid = (
    try(trimspace(var.fdp_gid), "") == "" ? (
      data.aws_region.this.region == element(keys(var.fdp_backend_bucket), 0)
      ? random_id.this.hex : data.terraform_remote_state.iam.0.outputs.fdp_gid
    ) : var.fdp_gid
  )
  ips = {
    for val in jsondecode(data.http.this.response_body)["prefixes"] : lower(val["service"]) => val... if(
      lower(val["service"]) == "codebuild" && (
        val["region"] == element(keys(var.fdp_backend_bucket), 0)
        || val["region"] == element(keys(var.fdp_backend_bucket), 1)
      )
    )
  }
  policy_ips  = local.ips["codebuild"].*.ip_prefix
  policy_arns = [format("arn:%s:iam::aws:policy/AdministratorAccess", data.aws_partition.this.partition)]
}
