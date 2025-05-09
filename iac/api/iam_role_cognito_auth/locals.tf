# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

locals {
  fdp_gid = (
    try(trimspace(var.fdp_gid), "") == ""
    ? data.terraform_remote_state.s3.outputs.fdp_gid : var.fdp_gid
  )
  external_id = uuidv5("743ac3c0-3bf7-4a5b-9e6c-59360447c757", var.q.name)
  policy_arns = [
    "arn:aws:iam::aws:policy/AmazonSNSFullAccess"
  ]
}
