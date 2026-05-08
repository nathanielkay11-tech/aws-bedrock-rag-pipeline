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

  # Normalise the model ID into a full ARN. Handles both bare IDs
  # (anthropic.claude-3-sonnet-…) and pre-built ARNs (cross-region profiles).
  bedrock_model_arn = startswith(var.bedrock_model_id, "arn:") ? var.bedrock_model_id : "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.bedrock_model_id}"

  # The AOSS collection is managed outside Terraform state to avoid
  # aoss:ListTagsForResource calls during refresh. ARN is fixed after creation.
  collection_arn = "arn:aws:aoss:eu-west-1:251478237846:collection/hhiu3f87s5ddcodbmm13"
}

data "aws_caller_identity" "current" {}
