# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

data "terraform_remote_state" "s3" {
  count = (
    data.aws_region.this.region == element(keys(var.fdp_backend_bucket), 1)
    && data.aws_region.this.region != local.region ? 1 : 0
  )
  backend = "s3"
  config = {
    skip_region_validation = true

    region = element(keys(var.fdp_backend_bucket), 0)
    bucket = var.fdp_backend_bucket[element(keys(var.fdp_backend_bucket), 0)]
    key    = format(var.fdp_backend_pattern, "s3_runtime")
  }
}
