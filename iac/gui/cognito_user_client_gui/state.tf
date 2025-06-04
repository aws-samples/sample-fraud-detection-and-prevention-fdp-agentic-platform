# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

output "client_id" {
  value = aws_cognito_user_pool_client.this.id
}

output "id" {
  value = aws_secretsmanager_secret.this.id
}

output "arn" {
  value = aws_secretsmanager_secret.this.arn
}

output "replica" {
  value = aws_secretsmanager_secret.this.replica
}

output "version_id" {
  value = aws_secretsmanager_secret_version.this.id
}

output "version_arn" {
  value = aws_secretsmanager_secret_version.this.arn
}

output "secret_name" {
  value = aws_secretsmanager_secret.this.name
}

output "user_pool_id" {
  value     = local.secret["FDP_TFVAR_COGNITO_USER_POOL_ID"]
  sensitive = true
}

output "user_pool_endpoint" {
  value     = local.secret["FDP_TFVAR_COGNITO_IDP_URL"]
  sensitive = true
}

output "api_client_id" {
  value     = local.secret["FDP_TFVAR_COGNITO_USER_POOL_ID"]
  sensitive = true
}
