# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

resource "aws_vpc_endpoint" "gw" {
  count             = length(local.gateways)
  vpc_id            = data.terraform_remote_state.sgr.outputs.vpc_id
  vpc_endpoint_type = "Gateway"
  service_name      = format("com.amazonaws.%s.%s", data.aws_region.this.region, element(local.gateways, count.index))
  route_table_ids = values({
    for key, val in local.route_table_ids :
    key => val if val != ""
  })
}

resource "aws_vpc_endpoint" "this" {
  count               = try(trimspace(element(local.interfaces, 0)), "") != "" ? length(local.interfaces) : 0
  vpc_id              = data.terraform_remote_state.sgr.outputs.vpc_id
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = var.q.private
  service_name        = format("com.amazonaws.%s.%s", data.aws_region.this.region, element(local.interfaces, count.index))
  subnet_ids          = local.subnet_ids
  security_group_ids  = [data.terraform_remote_state.sgr.outputs.id]
  depends_on          = [aws_vpc_endpoint.gw]
}
