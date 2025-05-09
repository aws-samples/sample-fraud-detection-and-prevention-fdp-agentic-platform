# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

variable "q" {
  type = map(string)
}

variable "allowed_oauth_flows" {
  type = list(string)
}

variable "allowed_oauth_scopes" {
  type = list(string)
}

variable "supported_identity_providers" {
  type = list(string)
}

variable "explicit_auth_flows" {
  type = list(string)
}
