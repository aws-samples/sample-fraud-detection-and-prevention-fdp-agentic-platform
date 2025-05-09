# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

locals {
  igw_ids = var.fdp_subnets_igw_create ? aws_subnet.igw.*.id : data.aws_subnets.igw.ids
  igw_map = {
    for i in split(",", var.fdp_subnets_igw_mapping) :
    element(split(":", i), 0) => element(split(":", i), 1) if(
      contains(data.terraform_remote_state.sgr.outputs.az_ids, element(split(":", i), 0))
    )
  }
  igw_filters = [
    {
      name   = local.igw_map == {} ? "availability-zone-id" : "cidr-block"
      values = local.igw_map == {} ? slice(data.terraform_remote_state.sgr.outputs.az_ids, 0, 3) : values(local.igw_map)
    },
    {
      name   = "default-for-az"
      values = [data.terraform_remote_state.sgr.outputs.vpc_default]
    },
    {
      name   = "vpc-id"
      values = [data.terraform_remote_state.sgr.outputs.vpc_id]
    }
  ]
  nat_ids = var.fdp_subnets_nat_create ? aws_subnet.nat.*.id : data.aws_subnets.nat.ids
  nat_map = {
    for i in split(",", var.fdp_subnets_nat_mapping) :
    element(split(":", i), 0) => element(split(":", i), 1) if(
      contains(data.terraform_remote_state.sgr.outputs.az_ids, element(split(":", i), 0))
    )
  }
  nat_filters = [
    {
      name   = "cidr-block"
      values = local.nat_map == {} ? [] : values(local.nat_map)
    },
    {
      name   = "vpc-id"
      values = [data.terraform_remote_state.sgr.outputs.vpc_id]
    }
  ]
}
