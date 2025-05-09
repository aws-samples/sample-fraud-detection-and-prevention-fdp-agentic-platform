# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

output "arn" {
  value = aws_wafv2_web_acl.this.arn
}

output "id" {
  value = aws_wafv2_web_acl.this.id
}

output "capacity" {
  value = aws_wafv2_web_acl.this.capacity
}
