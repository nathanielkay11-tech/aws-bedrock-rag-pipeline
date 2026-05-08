resource "aws_bedrockagent_knowledge_base" "legal" {
  provider = aws.no_tags
  name     = var.knowledge_base_name
  role_arn = aws_iam_role.bedrock_kb.arn

  # Bedrock validates the role's permissions at creation time; the inline policy
  # must be fully attached before this resource is created or it fails with access denied.
  depends_on = [aws_iam_role_policy_attachment.bedrock_kb]

  knowledge_base_configuration {
    type = "VECTOR"
    vector_knowledge_base_configuration {
      embedding_model_arn = "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.titan-embed-text-v2:0"
    }
  }

  storage_configuration {
    type = "OPENSEARCH_SERVERLESS"
    opensearch_serverless_configuration {
      collection_arn    = local.collection_arn
      vector_index_name = "legal-contracts-index"
      field_mapping {
        vector_field   = "embedding"
        text_field     = "text"
        metadata_field = "metadata"
      }
    }
  }
}

resource "aws_bedrockagent_data_source" "contracts" {
  name                 = "legal-contracts-s3"
  knowledge_base_id    = aws_bedrockagent_knowledge_base.legal.id
  data_deletion_policy = "RETAIN"

  data_source_configuration {
    type = "S3"
    s3_configuration {
      bucket_arn = aws_s3_bucket.documents.arn
    }
  }
}
