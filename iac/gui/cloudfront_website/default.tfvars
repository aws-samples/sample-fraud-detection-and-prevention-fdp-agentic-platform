# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

q = {
  description  = "FDP WEBSITE"
  logs_prefix  = "cdn_website_logs/"
  cache_viewer = "https-only"
  default_ttl  = 3600
  max_ttl      = 86400
  min_ttl      = 0
}
