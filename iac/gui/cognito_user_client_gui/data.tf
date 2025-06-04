# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

data "aws_secretsmanager_secret" "this" {
  name = format("%s-%s-%s", var.q.secret_search, data.aws_region.this.name, local.fdp_gid)
}

data "aws_secretsmanager_secret_version" "this" {
  secret_id = data.aws_secretsmanager_secret.this.id
}

data "terraform_remote_state" "s3" {
  backend = "s3"
  config = {
    skip_region_validation = true

    region = data.aws_region.this.name
    bucket = var.fdp_backend_bucket[data.aws_region.this.name]
    key    = format(var.fdp_backend_pattern, "s3_website")
  }
}
