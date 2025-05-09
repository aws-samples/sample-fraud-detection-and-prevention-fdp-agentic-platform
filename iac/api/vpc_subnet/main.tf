# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

##########################
# IGW = Internet Gateway #
##########################
resource "aws_subnet" "igw" {
  count                = var.fdp_subnets_igw_create ? length(values(local.igw_map)) : 0
  vpc_id               = data.terraform_remote_state.sgr.outputs.vpc_id
  cidr_block           = element(values(local.igw_map), count.index)
  availability_zone_id = element(keys(local.igw_map), count.index)
}

resource "aws_internet_gateway" "igw" {
  count  = var.fdp_subnets_igw_create ? 1 : 0
  vpc_id = data.terraform_remote_state.sgr.outputs.vpc_id
}

resource "aws_route_table" "igw" {
  count  = var.fdp_subnets_igw_create ? 1 : 0
  vpc_id = data.terraform_remote_state.sgr.outputs.vpc_id
}

resource "aws_route" "igw" {
  count                  = var.fdp_subnets_igw_create ? 1 : 0
  route_table_id         = element(aws_route_table.igw.*.id, 0)
  gateway_id             = element(aws_internet_gateway.igw.*.id, 0)
  destination_cidr_block = "0.0.0.0/0"
}

resource "aws_route_table_association" "igw" {
  count          = var.fdp_subnets_igw_create ? length(local.igw_ids) : 0
  subnet_id      = element(local.igw_ids, count.index)
  route_table_id = element(aws_route_table.igw.*.id, 0)
}

#############################################
# NAT = Network Address Translation Gateway #
#############################################
resource "aws_subnet" "nat" {
  count                = var.fdp_subnets_nat_create ? length(values(local.nat_map)) : 0
  vpc_id               = data.terraform_remote_state.sgr.outputs.vpc_id
  cidr_block           = element(values(local.nat_map), count.index)
  availability_zone_id = element(keys(local.nat_map), count.index)
}

resource "aws_eip" "nat" {
  count  = var.fdp_subnets_nat_create ? 1 : 0
  domain = "vpc"
}

resource "aws_nat_gateway" "nat" {
  count         = var.fdp_subnets_nat_create ? 1 : 0
  allocation_id = element(aws_eip.nat.*.id, 0)
  subnet_id     = element(local.igw_ids, 0)
  depends_on    = [aws_internet_gateway.igw]
}

resource "aws_route_table" "nat" {
  count  = var.fdp_subnets_nat_create ? 1 : 0
  vpc_id = data.terraform_remote_state.sgr.outputs.vpc_id
}

resource "aws_route" "nat" {
  count                  = var.fdp_subnets_nat_create ? 1 : 0
  route_table_id         = element(aws_route_table.nat.*.id, 0)
  nat_gateway_id         = element(aws_nat_gateway.nat.*.id, 0)
  destination_cidr_block = "0.0.0.0/0"
}

resource "aws_route_table_association" "nat" {
  count          = var.fdp_subnets_nat_create ? length(local.nat_ids) : 0
  subnet_id      = element(local.nat_ids, count.index)
  route_table_id = element(aws_route_table.nat.*.id, 0)
}
