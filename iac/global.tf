# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

data "aws_region" "this" {}
data "aws_partition" "this" {}
data "aws_caller_identity" "this" {}

provider "aws" {
  allowed_account_ids    = try(trimspace(var.fdp_account), "") != "" ? split(",", var.fdp_account) : null
  skip_region_validation = true

  default_tags {
    tags = {
      project        = "fraud-detection-prevention"
      environment    = "default"
      contact        = "github.com/eistrati"
      globalId       = try(trimspace(var.fdp_gid), "") != "" ? var.fdp_gid : null
      awsApplication = try(trimspace(var.fdp_app_arn), "") != "" ? var.fdp_app_arn : null
    }
  }
}

terraform {
  required_version = ">= 1.11.0, <1.13.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.98.0"
    }
  }
}

variable "fdp_region" {
  type        = string
  description = "AWS region (e.g. us-east-1)"
  default     = ""
}

variable "fdp_bucket" {
  type        = string
  description = "S3 bucket (e.g. fdp-backend-us-east-1)"
  default     = ""
}

variable "fdp_website" {
  type        = string
  description = "S3 website (e.g. fdp-website-us-east-1)"
  default     = ""
}

variable "fdp_backend_create" {
  type        = bool
  description = "Create S3 bucket for terraform backend (if true, otherwise reuse the existing ones)"
  default     = false
}

variable "fdp_backend_bucket" {
  type        = map(string)
  description = "S3 bucket for terraform backend in each supported AWS region"
  default = {
    "us-east-1" = "fdp-backend-us-east-1"
    "us-west-2" = "fdp-backend-us-west-2"
  }
}

variable "fdp_backend_pattern" {
  type        = string
  description = "S3 path pattern for terraform backend"
  default     = "terraform/github/fdp/%s/terraform.tfstate"
}

variable "fdp_gid" {
  type        = string
  description = "Global ID appended to AWS resource names (e.g. abcd1234)"
  default     = ""
}

variable "fdp_account" {
  type        = string
  description = "Allowed AWS account ID (or IDs, separated by comma)"
  default     = ""
}

variable "fdp_app_arn" {
  type        = string
  description = "AWS myApplication ARN (e.g. arn:{{partition}}:resource-groups:{{region_name}}:{{account_id}}:group/{{app_id}})"
  default     = ""
}

variable "fdp_app_name" {
  type        = string
  description = "AWS myApplication Name (e.g. fdp)"
  default     = "fdp"
}

variable "fdp_custom_domain" {
  type        = string
  description = "Custom Domain (e.g. example.com)"
  default     = ""
}

variable "fdp_vpc_id" {
  type        = string
  description = "VPC ID (must already exist, otherwise falls back to the default vpc)"
  default     = ""
}

variable "fdp_vpce_mapping" {
  type        = string
  description = "VPC endpoints mapping (e.g. {{interface_name}},{{interface_name}})"
  default     = ""
}

variable "fdp_subnets_igw_create" {
  type        = bool
  description = "Create public subnets (if true, otherwise reuse the existing ones)"
  default     = false
}

variable "fdp_subnets_nat_create" {
  type        = bool
  description = "Create private subnets (if true, otherwise reuse the existing ones)"
  default     = false
}

variable "fdp_subnets_igw_mapping" {
  type        = string
  description = "Public subnets mapping (e.g. {{availability_zone_id}}:{{availability_zone_cidr}},{{local_zone_id}}:{{local_zone_cidr}})"
  default     = ""
}

variable "fdp_subnets_nat_mapping" {
  type        = string
  description = "Private subnets mapping (e.g. {{availability_zone_id}}:{{availability_zone_cidr}},{{local_zone_id}}:{{local_zone_cidr}})"
  default     = ""
}
