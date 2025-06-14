# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

q = {
  security_policy     = "TLS_1_2"
  base_path_healthy   = null
  base_path_unhealthy = "unhealthy"
  secret_name         = "fdp-api-secrets"
  description         = "FDP API SECRETS"
  force_overwrite     = true
  recovery_in_days    = 0
}

types = ["REGIONAL"]
