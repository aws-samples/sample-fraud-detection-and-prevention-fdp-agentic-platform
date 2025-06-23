# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

resource "aws_dynamodb_table" "this" {
  #checkov:skip=CKV_AWS_28:This solution leverages DynamoDB point in time recovery / backup (false positive)
  #checkov:skip=CKV_AWS_119:This solution leverages KMS encryption using AWS managed keys instead of CMKs (false positive)
  #checkov:skip=CKV2_AWS_16:This solution does not leverages DynamoDB auto-scaling capabilities (false positive)

  count            = data.aws_region.this.region == element(keys(var.fdp_backend_bucket), 0) ? length(var.r) : 0
  name             = format("%s-%s", var.r[count.index]["name"], local.fdp_gid)
  hash_key         = strcontains(var.r[count.index]["attr"], var.q.hash_key) ? var.q.hash_key : null
  range_key        = strcontains(var.r[count.index]["attr"], var.q.range_key) ? var.q.range_key : null
  billing_mode     = var.q.billing_mode
  stream_enabled   = var.q.stream_enabled
  stream_view_type = var.q.stream_view_type

  dynamic "attribute" {
    for_each = [for attr in local.attributes : attr if strcontains(var.r[count.index]["attr"], attr.name)]
    content {
      name = attribute.value.name
      type = attribute.value.type
    }
  }

  dynamic "replica" {
    for_each = local.replicas
    content {
      region_name    = replica.value
      propagate_tags = true
    }
  }

  point_in_time_recovery {
    enabled = var.q.point_in_time_recovery
  }

  server_side_encryption {
    enabled = var.q.encryption_enabled
  }

  # ttl {
  #   enabled        = var.q.ttl_enabled
  #   attribute_name = var.q.ttl_attribute_name
  # }

  lifecycle {
    create_before_destroy = true
    ignore_changes        = [replica, read_capacity, write_capacity]
  }
}
