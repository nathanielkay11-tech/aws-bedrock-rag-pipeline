# Set this value as CONFIG.API_BASE_URL in src/frontend/index.html
output "api_gateway_url" {
  description = "API Gateway invoke URL — use as CONFIG.API_BASE_URL in the frontend (no trailing slash)"
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "knowledge_base_id" {
  description = "Bedrock Knowledge Base ID"
  value       = aws_bedrockagent_knowledge_base.legal.id
}

output "data_source_id" {
  description = "Bedrock Knowledge Base Data Source ID"
  value       = aws_bedrockagent_data_source.contracts.data_source_id
}

output "s3_bucket_name" {
  description = "S3 bucket for document uploads"
  value       = aws_s3_bucket.documents.bucket
}

output "query_lambda_name" {
  description = "Query Lambda function name"
  value       = aws_lambda_function.rag_query.function_name
}

output "ingestion_lambda_name" {
  description = "Ingestion Lambda function name"
  value       = aws_lambda_function.ingestion.function_name
}

output "collection_arn" {
  description = "OpenSearch Serverless collection ARN"
  value       = local.collection_arn
}
