terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
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

locals {
  collection_name = "${var.environment}-legal-kb"
}

data "aws_caller_identity" "current" {}
