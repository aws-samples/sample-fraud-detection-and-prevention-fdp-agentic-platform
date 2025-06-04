# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

output "arn" {
  value = aws_cognito_identity_pool.this.arn
}

output "id" {
  value = aws_cognito_identity_pool.this.id
}

# output "client_id" {
#   value = data.terraform_remote_state.client.outputs.client_id
# }

# output "api_client_id" {
#   value = data.terraform_remote_state.client.outputs.api_client_id
# }

# output "client_endpoint" {
#   value = replace(data.terraform_remote_state.client.outputs.user_pool_endpoint, "https://", "")
# }
