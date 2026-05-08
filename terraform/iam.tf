# ---------------------------------------------------------------------------
# Bedrock Knowledge Base role
# ---------------------------------------------------------------------------

resource "aws_iam_role" "bedrock_kb" {
  name = "${var.environment}-bedrock-kb-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "bedrock.amazonaws.com" }
        Action    = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}

resource "aws_iam_policy" "bedrock_kb" {
  name = "${var.environment}-bedrock-kb-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3Read"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:ListBucket"]
        Resource = [
          aws_s3_bucket.documents.arn,
          "${aws_s3_bucket.documents.arn}/*",
        ]
      },
      {
        Sid      = "BedrockEmbed"
        Effect   = "Allow"
        Action   = "bedrock:InvokeModel"
        Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.titan-embed-text-v2:0"
      },
      {
        Sid      = "OpenSearchServerless"
        Effect   = "Allow"
        Action   = "aoss:APIAccessAll"
        Resource = local.collection_arn
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "bedrock_kb" {
  role       = aws_iam_role.bedrock_kb.name
  policy_arn = aws_iam_policy.bedrock_kb.arn
}

# ---------------------------------------------------------------------------
# Query Lambda role
# ---------------------------------------------------------------------------

resource "aws_iam_role" "lambda" {
  name = "${var.environment}-rag-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "lambda_bedrock" {
  name = "${var.environment}-lambda-bedrock-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BedrockRAG"
        Effect = "Allow"
        Action = [
          "bedrock:RetrieveAndGenerate",
          "bedrock:Retrieve",
        ]
        Resource = aws_bedrockagent_knowledge_base.legal.arn
      },
      {
        Sid      = "BedrockInvokeModel"
        Effect   = "Allow"
        Action   = "bedrock:InvokeModel"
        Resource = local.bedrock_model_arn
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_bedrock" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.lambda_bedrock.arn
}

# ---------------------------------------------------------------------------
# Ingestion Lambda role
# ---------------------------------------------------------------------------

resource "aws_iam_role" "ingestion_lambda" {
  name = "${var.environment}-ingestion-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ingestion_lambda_basic" {
  role       = aws_iam_role.ingestion_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "ingestion_lambda_bedrock" {
  name = "${var.environment}-ingestion-lambda-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BedrockIngestion"
        Effect = "Allow"
        Action = [
          "bedrock:StartIngestionJob",
          "bedrock:GetIngestionJob",
        ]
        Resource = aws_bedrockagent_knowledge_base.legal.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ingestion_lambda_bedrock" {
  role       = aws_iam_role.ingestion_lambda.name
  policy_arn = aws_iam_policy.ingestion_lambda_bedrock.arn
}

# ---------------------------------------------------------------------------
# Presign Lambda role — only needs s3:PutObject because the URL it generates
# is signed with these credentials; S3 validates them on the browser's PUT.
# ---------------------------------------------------------------------------

resource "aws_iam_role" "presign_lambda" {
  name = "${var.environment}-presign-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

# CloudWatch Logs access for the presign Lambda
resource "aws_iam_role_policy_attachment" "presign_lambda_basic" {
  role       = aws_iam_role.presign_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Allow the presign Lambda to sign PUT requests for any key under matters/
resource "aws_iam_policy" "presign_lambda_s3" {
  name = "${var.environment}-presign-lambda-s3-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "S3PresignPut"
        Effect   = "Allow"
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.documents.arn}/matters/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "presign_lambda_s3" {
  role       = aws_iam_role.presign_lambda.name
  policy_arn = aws_iam_policy.presign_lambda_s3.arn
}
