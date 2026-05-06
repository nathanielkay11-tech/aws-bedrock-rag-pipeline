# ---------------------------------------------------------------------------
# Build artifacts — zip source files so terraform apply is self-contained.
# boto3 is pre-installed in Lambda's Python 3.12 runtime; no bundling needed.
# ---------------------------------------------------------------------------
data "archive_file" "query_lambda" {
  type        = "zip"
  source_file = "${path.module}/../src/query_handler.py"
  output_path = "${path.module}/query_lambda.zip"
}

data "archive_file" "ingestion_lambda" {
  type        = "zip"
  source_file = "${path.module}/../src/ingestion_handler.py"
  output_path = "${path.module}/ingestion_lambda.zip"
}

# ---------------------------------------------------------------------------
# CloudWatch log groups — pre-create to control retention
# ---------------------------------------------------------------------------
resource "aws_cloudwatch_log_group" "query_lambda" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "ingestion_lambda" {
  name              = "/aws/lambda/${var.lambda_function_name}-ingestion"
  retention_in_days = 30
}

# ---------------------------------------------------------------------------
# Query Lambda — answers questions via Bedrock RetrieveAndGenerate
# ---------------------------------------------------------------------------
resource "aws_lambda_function" "rag_query" {
  function_name    = var.lambda_function_name
  role             = aws_iam_role.lambda.arn
  filename         = data.archive_file.query_lambda.output_path
  source_code_hash = data.archive_file.query_lambda.output_base64sha256
  handler          = "query_handler.lambda_handler"
  runtime          = "python3.12"
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory

  environment {
    variables = {
      KNOWLEDGE_BASE_ID = aws_bedrockagent_knowledge_base.legal.id
      BEDROCK_MODEL_ID  = var.bedrock_model_id
      BEDROCK_REGION    = var.aws_region
      S3_BUCKET_NAME    = aws_s3_bucket.documents.bucket
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.query_lambda,
    aws_iam_role_policy_attachment.lambda_basic,
  ]
}

# ---------------------------------------------------------------------------
# Ingestion Lambda — triggered by S3 uploads to sync the knowledge base
# ---------------------------------------------------------------------------
resource "aws_lambda_function" "ingestion" {
  function_name    = "${var.lambda_function_name}-ingestion"
  role             = aws_iam_role.ingestion_lambda.arn
  filename         = data.archive_file.ingestion_lambda.output_path
  source_code_hash = data.archive_file.ingestion_lambda.output_base64sha256
  handler          = "ingestion_handler.lambda_handler"
  runtime          = "python3.12"
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory

  environment {
    variables = {
      KNOWLEDGE_BASE_ID = aws_bedrockagent_knowledge_base.legal.id
      DATA_SOURCE_ID    = aws_bedrockagent_data_source.contracts.data_source_id
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.ingestion_lambda,
    aws_iam_role_policy_attachment.ingestion_lambda_basic,
  ]
}

# ---------------------------------------------------------------------------
# S3 → Lambda trigger — grant S3 permission to invoke the ingestion Lambda,
# then configure the bucket notification for all ObjectCreated events under
# the matters/ prefix.
# ---------------------------------------------------------------------------
resource "aws_lambda_permission" "s3_invoke_ingestion" {
  statement_id   = "AllowS3Invoke"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.ingestion.function_name
  principal      = "s3.amazonaws.com"
  source_arn     = aws_s3_bucket.documents.arn
  source_account = data.aws_caller_identity.current.account_id
}

resource "aws_s3_bucket_notification" "ingestion_trigger" {
  bucket = aws_s3_bucket.documents.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.ingestion.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "matters/"
  }

  depends_on = [aws_lambda_permission.s3_invoke_ingestion]
}
