# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

q = {
  bucket           = "fdp-website"
  force_destroy    = true
  object_ownership = "BucketOwnerPreferred"
  logs_prefix      = "s3_website_logs/"
  index_document   = "index.html"
  error_document   = "index.html"
}
