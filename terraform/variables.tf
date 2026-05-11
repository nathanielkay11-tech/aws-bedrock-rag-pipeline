# AWS region where all resources will be deployed
variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "eu-west-1"
}

# Deployment environment used for resource naming and tagging
variable "environment" {
  description = "Deployment environment (e.g. dev, staging, prod)"
  type        = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{0,18}[a-z0-9]$", var.environment))
    error_message = "environment must be 2–20 lowercase letters, digits, or hyphens, and must start with a letter."
  }
}

# Name of the S3 bucket that stores raw legal contract documents
variable "s3_bucket_name" {
  description = "Name of the S3 bucket used as the Bedrock knowledge base data source"
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.s3_bucket_name))
    error_message = "s3_bucket_name must be 3–63 characters, lowercase letters/digits/hyphens/dots only, and must start and end with a letter or digit."
  }
}

# Display name for the Bedrock Knowledge Base resource
variable "knowledge_base_name" {
  description = "Name of the Bedrock Knowledge Base for legal contract Q&A"
  type        = string
}

# Name of the Lambda function that handles Q&A query requests
variable "lambda_function_name" {
  description = "Name of the Lambda function that queries the Bedrock knowledge base"
  type        = string
}

# Maximum execution time for the Lambda function in seconds
variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 30
  validation {
    condition     = var.lambda_timeout >= 1 && var.lambda_timeout <= 900
    error_message = "lambda_timeout must be between 1 and 900 seconds."
  }
}

# Memory allocated to the Lambda function in MB
variable "lambda_memory" {
  description = "Lambda function memory allocation in MB"
  type        = number
  default     = 512
  validation {
    condition     = var.lambda_memory >= 128 && var.lambda_memory <= 10240 && var.lambda_memory % 64 == 0
    error_message = "lambda_memory must be between 128 and 10240 MB and a multiple of 64."
  }
}

# Bedrock foundation model used for response generation
variable "bedrock_model_id" {
  description = "ID of the Bedrock foundation model used for RAG responses"
  type        = string
  default = "eu.anthropic.claude-sonnet-4-5-20250929-v1:0"
}
