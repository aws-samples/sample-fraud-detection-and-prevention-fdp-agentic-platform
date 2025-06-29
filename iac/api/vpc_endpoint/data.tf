# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

data "aws_ec2_managed_prefix_list" "this" {
  count = try(trimspace(element(local.gateways, 0)), "") != "" ? length(local.gateways) : 0
  name  = format("com.amazonaws.%s.%s", data.aws_region.this.region, element(local.gateways, count.index))
}

data "terraform_remote_state" "sgr" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.region
    bucket = var.fdp_backend_bucket[data.aws_region.this.region]
    key    = format(var.fdp_backend_pattern, "security_group")
  }
}

data "terraform_remote_state" "subnet" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.region
    bucket = var.fdp_backend_bucket[data.aws_region.this.region]
    key    = format(var.fdp_backend_pattern, "vpc_subnet")
  }
}
