# CloudWatch log group created before the function to control retention
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 30
}

resource "aws_lambda_function" "rag_query" {
  function_name = var.lambda_function_name
  role          = aws_iam_role.lambda.arn

  # Replace with the actual build artifact before applying
  filename         = "${path.module}/lambda.zip"
  handler          = "handler.lambda_handler"
  runtime          = "python3.12"
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory

  environment {
    variables = {
      KNOWLEDGE_BASE_ID = aws_bedrockagent_knowledge_base.legal.id
      BEDROCK_MODEL_ID  = var.bedrock_model_id
      # AWS_REGION is reserved by the Lambda runtime; use a distinct name
      BEDROCK_REGION    = var.aws_region
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda,
    aws_iam_role_policy_attachment.lambda_basic,
  ]
}
