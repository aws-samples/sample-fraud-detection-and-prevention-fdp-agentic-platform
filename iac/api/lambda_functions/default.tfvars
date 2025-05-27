# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

q = {
  package_type = "Zip"    # "Image"
  architecture = "x86_64" # "arm64"
  handler      = "function.handler"
  runtime      = "python3.11"
  memory_size  = 128
  timeout      = 15
  storage_size = 512
  tracing_mode = "PassThrough"
  public       = null
  logging      = "INFO"

  sqs_managed_sse_enabled = true
  secrets_manager_ttl     = 300

  log_group_exists  = false
  retention_in_days = 5
  skip_destroy      = false
}

r = [{
  key  = "agent"
  name = "fdp-lambda-agent"
  desc = "FDP LAMBDA AGENT"
  path = "../../../app/api/agent-manager"
  file = "lib/requirements.txt"
  }, {
  key  = "config"
  name = "fdp-lambda-config"
  desc = "FDP LAMBDA CONFIG"
  path = "../../../app/api/configuration-manager"
  file = "lib/requirements.txt"
  # }, {
  # key  = "flow"
  # name = "fdp-lambda-flow"
  # desc = "FDP LAMBDA FLOW"
  # path = "../../../app/api/flow-manager"
  # file = "requirements.txt"
  }, {
  key  = "prompt"
  name = "fdp-lambda-prompt"
  desc = "FDP LAMBDA PROMPT"
  path = "../../../app/api/prompt-manager"
  file = "lib/requirements.txt"
  }, {
  key  = "token"
  name = "fdp-user-pool"
  desc = "FDP LAMBDA TOKEN"
  path = "../../../app/api/pre-token-generator"
  file = "lib/requirements.txt"
}]
