# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

output "arn" {
  value = aws_security_group.this.arn
}

output "id" {
  value = aws_security_group.this.id
}

output "vpc_id" {
  value = aws_security_group.this.vpc_id
}

output "vpc_default" {
  value = data.aws_vpc.this.default
}

output "az_ids" {
  value = data.aws_availability_zones.az.zone_ids
}

output "az_names" {
  value = data.aws_availability_zones.az.names
}
