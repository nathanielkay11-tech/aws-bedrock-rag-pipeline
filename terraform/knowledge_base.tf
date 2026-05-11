resource "aws_bedrockagent_knowledge_base" "legal" {
  provider = aws.no_tags
  name     = var.knowledge_base_name
  role_arn = aws_iam_role.bedrock_kb.arn

  # Bedrock validates the role's permissions at creation time; the inline policy
  # must be fully attached before this resource is created or it fails with access denied.
  depends_on = [
    aws_iam_role_policy_attachment.bedrock_kb,
    aws_opensearchserverless_access_policy.bedrock_kb,
    null_resource.opensearch_index,
  ]

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

# ---------------------------------------------------------------------------
# OpenSearch vector index — runs on every apply so the index always exists
# before the Knowledge Base is created or refreshed. Safe to re-run: the
# Python script is idempotent and skips creation when the index is present.
# ---------------------------------------------------------------------------
resource "null_resource" "opensearch_index" {
  # timestamp() changes on every plan, forcing this to re-run each apply.
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = "python3 -m pip install -q opensearch-py requests-aws4auth && python3 '${path.module}/../scripts/create_opensearch_index.py'"

    environment = {
      COLLECTION_ENDPOINT = local.collection_endpoint
      AWS_REGION          = var.aws_region
      INDEX_NAME          = "legal-contracts-index"
    }
  }

  # Access policy must exist before we can write to the collection.
  depends_on = [aws_opensearchserverless_access_policy.bedrock_kb]
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
