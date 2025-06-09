# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

q = {
  hash_key     = "pk"
  hash_type    = "S"
  range_key    = "sk"
  range_type   = "S"
  billing_mode = "PAY_PER_REQUEST"

  stream_enabled         = true
  stream_view_type       = "NEW_AND_OLD_IMAGES"
  point_in_time_recovery = true
  encryption_enabled     = true
  ttl_enabled            = false
  ttl_attribute_name     = "ttl_time"
}

r = [{
  key  = "agent"
  name = "fdp-agent"
  attr = "pk"
  }, {
  key  = "config"
  name = "fdp-config"
  attr = "pk,sk"
  }, {
  key  = "prompt"
  name = "fdp-prompt"
  attr = "pk"
  }, {
  key  = "agent2"
  name = "fdp-agent-verifications"
  attr = "pk"
  }, {
  key  = "strands"
  name = "fdp-strands"
  attr = "pk"
}]
