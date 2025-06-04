# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

q = {
  name                             = "fdp-identity-pool"
  allow_unauthenticated_identities = false
  allow_classic_flow               = false
  server_side_token_check          = false
  secret_name                      = "fdp-gui-secrets"
  description                      = "FDP GUI SECRETS"
  force_overwrite                  = true
  recovery_in_days                 = 0
}
