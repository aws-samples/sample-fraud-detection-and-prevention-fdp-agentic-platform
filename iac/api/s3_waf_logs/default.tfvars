# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

q = {
  bucket           = "fdp"
  force_destroy    = true
  object_ownership = "BucketOwnerPreferred"
  logs_prefix      = "s3_waf_logs/"
}
