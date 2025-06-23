# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

resource "aws_iam_role" "this" {
  name               =  format("%s-%s-%s", var.q.name, data.aws_region.this.region, local.fdp_gid)
  description        = var.q.description
  path               = var.q.path
  assume_role_policy = data.aws_iam_policy_document.this.json

  lifecycle {
    create_before_destroy = true
  }
}
