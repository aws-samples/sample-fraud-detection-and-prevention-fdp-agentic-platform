# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

resource "aws_iam_role" "this" {
  name               = format("%s-%s-%s", var.q.name, data.aws_region.this.region, local.fdp_gid)
  description        = var.q.description
  path               = var.q.path
  assume_role_policy = data.aws_iam_policy_document.role.json

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_iam_policy" "this" {
  name        = format("%s-%s-%s", var.q.name, data.aws_region.this.region, local.fdp_gid)
  description = var.q.description
  path        = var.q.path
  policy      = data.aws_iam_policy_document.policy.json

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_iam_role_policy_attachment" "this" {
  role       = aws_iam_role.this.name
  policy_arn = aws_iam_policy.this.arn
}
