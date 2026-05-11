terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = "bedrock-rag-legal"
      ManagedBy   = "terraform"
    }
  }
}

# Used for resources whose TagResource action is not granted on this deployment user
provider "aws" {
  alias  = "no_tags"
  region = var.aws_region
}

locals {
  collection_name = "${var.environment}-legal-kb"

  # Build the IAM resource ARN for the model. Cross-region inference profiles
  # (eu.* / us.* / ap.*) use the inference-profile path; bare foundation model
  # IDs use foundation-model; pre-built ARNs are passed through unchanged.
  bedrock_model_arn = (
    startswith(var.bedrock_model_id, "arn:")
    ? var.bedrock_model_id
    : can(regex("^(eu|us|ap)\\.", var.bedrock_model_id))
      ? "arn:aws:bedrock:${var.aws_region}::inference-profile/${var.bedrock_model_id}"
      : "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.bedrock_model_id}"
  )

  # The AOSS collection is managed outside Terraform state to avoid
  # aoss:ListTagsForResource calls during refresh. ARN is fixed after creation.
  collection_arn = "arn:aws:aoss:eu-west-1:251478237846:collection/u0hp7ktjncq6c4w9ejqg"

  # Derived from the collection ARN — used by the local-exec index provisioner.
  collection_id       = regex("collection/(.+)$", local.collection_arn)[0]
  collection_endpoint = "https://${local.collection_id}.${var.aws_region}.aoss.amazonaws.com"
}

data "aws_caller_identity" "current" {}
