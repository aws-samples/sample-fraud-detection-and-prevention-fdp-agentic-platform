# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

data "aws_vpcs" "this" {
  filter {
    name   = try(trimspace(var.fdp_vpc_id), "") != "" ? "vpc-id" : "tag:Name"
    values = [try(trimspace(var.fdp_vpc_id), "") != "" ? var.fdp_vpc_id : var.q.vpc_name]
  }
}

data "aws_vpc" "this" {
  id      = try(element(data.aws_vpcs.this.ids, 0), null)
  default = try(element(data.aws_vpcs.this.ids, 0), null) == null ? true : false
}

data "aws_availability_zones" "az" {
  filter {
    name   = "zone-type"
    values = ["availability-zone"]
  }
  filter {
    name   = "state"
    values = ["available"]
  }
}

data "terraform_remote_state" "s3" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.region
    bucket = var.fdp_backend_bucket[data.aws_region.this.region]
    key    = format(var.fdp_backend_pattern, "s3_runtime")
  }
}
