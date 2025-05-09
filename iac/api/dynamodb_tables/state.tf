# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

output "arn" {
  value = (
    length(aws_dynamodb_table.this.*.arn) > 0
    ? { for k, v in aws_dynamodb_table.this : var.r[k]["key"] => v.arn }
    : null
  )
}

output "id" {
  value = (
    length(aws_dynamodb_table.this.*.id) > 0
    ? { for k, v in aws_dynamodb_table.this : var.r[k]["key"] => v.id }
    : null
  )
}

output "stream_arn" {
  value = (
    length(aws_dynamodb_table.this.*.stream_arn) > 0
    ? { for k, v in aws_dynamodb_table.this : var.r[k]["key"] => v.stream_arn }
    : null
  )
}

output "stream_label" {
  value = (
    length(aws_dynamodb_table.this.*.stream_label) > 0
    ? { for k, v in aws_dynamodb_table.this : var.r[k]["key"] => v.stream_label }
    : null
  )
}
