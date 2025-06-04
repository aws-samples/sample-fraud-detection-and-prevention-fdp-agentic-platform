# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

output "arn" {
  value = aws_cognito_identity_pool.this.arn
}

output "id" {
  value = aws_cognito_identity_pool.this.id
}
