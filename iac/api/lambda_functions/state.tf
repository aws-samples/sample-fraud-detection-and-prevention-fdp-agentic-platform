# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

output "arn" {
  value = (
    length(module.lambda.*.lambda_function_arn) > 0
    ? { for k, v in module.lambda : var.r[k]["key"] => v.lambda_function_arn }
    : null
  )
}

output "invoke_arn" {
  value = (
    length(module.lambda.*.lambda_function_invoke_arn) > 0
    ? { for k, v in module.lambda : var.r[k]["key"] => v.lambda_function_invoke_arn }
    : null
  )
}

output "qualified_arn" {
  value = (
    length(module.lambda.*.lambda_function_qualified_arn) > 0
    ? { for k, v in module.lambda : var.r[k]["key"] => v.lambda_function_qualified_arn }
    : null
  )
}

output "qualified_invoke_arn" {
  value = (
    length(module.lambda.*.lambda_function_qualified_invoke_arn) > 0
    ? { for k, v in module.lambda : var.r[k]["key"] => v.lambda_function_qualified_invoke_arn }
    : null
  )
}

output "signing_job_arn" {
  value = (
    length(module.lambda.*.lambda_function_signing_job_arn) > 0
    ? { for k, v in module.lambda : var.r[k]["key"] => v.lambda_function_signing_job_arn }
    : null
  )
}

output "signing_profile_version_arn" {
  value = (
    length(module.lambda.*.lambda_function_signing_profile_version_arn) > 0
    ? { for k, v in module.lambda : var.r[k]["key"] => v.lambda_function_signing_profile_version_arn }
    : null
  )
}

output "last_modified" {
  value = (
    length(module.lambda.*.lambda_function_last_modified) > 0
    ? { for k, v in module.lambda : var.r[k]["key"] => v.lambda_function_last_modified }
    : null
  )
}

output "source_code_size" {
  value = (
    length(module.lambda.*.lambda_function_source_code_size) > 0
    ? { for k, v in module.lambda : var.r[k]["key"] => v.lambda_function_source_code_size }
    : null
  )
}

output "name" {
  value = (
    length(module.lambda.*.lambda_function_name) > 0
    ? { for k, v in module.lambda : var.r[k]["key"] => v.lambda_function_name }
    : null
  )
}

output "version" {
  value = (
    length(module.lambda.*.lambda_function_version) > 0
    ? { for k, v in module.lambda : var.r[k]["key"] => v.lambda_function_version }
    : null
  )
}
