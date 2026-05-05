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
}

# Name of the S3 bucket that stores raw legal contract documents
variable "s3_bucket_name" {
  description = "Name of the S3 bucket used as the Bedrock knowledge base data source"
  type        = string
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
}

# Memory allocated to the Lambda function in MB
variable "lambda_memory" {
  description = "Lambda function memory allocation in MB"
  type        = number
  default     = 512
}

# Bedrock foundation model used for response generation
variable "bedrock_model_id" {
  description = "ID of the Bedrock foundation model used for RAG responses"
  type        = string
  default     = "anthropic.claude-3-sonnet-20240229-v1:0"
}
