resource "aws_opensearchserverless_security_policy" "encryption" {
  name = "${var.environment}-kb-enc"
  type = "encryption"
  policy = jsonencode({
    Rules = [
      {
        Resource     = ["collection/${local.collection_name}"]
        ResourceType = "collection"
      }
    ]
    AWSOwnedKey = true
  })
}

# Public network access is required so Bedrock's service role can reach the collection
resource "aws_opensearchserverless_security_policy" "network" {
  name = "${var.environment}-kb-net"
  type = "network"
  policy = jsonencode([
    {
      Rules = [
        {
          Resource     = ["collection/${local.collection_name}"]
          ResourceType = "collection"
        }
      ]
      AllowFromPublic = true
    }
  ])
}

resource "aws_opensearchserverless_access_policy" "bedrock_kb" {
  name = "${var.environment}-kb-access"
  type = "data"
  policy = jsonencode([
    {
      Rules = [
        {
          Resource     = ["collection/${local.collection_name}"]
          ResourceType = "collection"
          Permission = [
            "aoss:CreateCollectionItems",
            "aoss:DeleteCollectionItems",
            "aoss:UpdateCollectionItems",
            "aoss:DescribeCollectionItems",
          ]
        },
        {
          Resource     = ["index/${local.collection_name}/*"]
          ResourceType = "index"
          Permission = [
            "aoss:CreateIndex",
            "aoss:DeleteIndex",
            "aoss:UpdateIndex",
            "aoss:DescribeIndex",
            "aoss:ReadDocument",
            "aoss:WriteDocument",
          ]
        }
      ]
      Principal = [aws_iam_role.bedrock_kb.arn]
    }
  ])
}

resource "aws_opensearchserverless_collection" "kb" {
  name = local.collection_name
  type = "VECTORSEARCH"

  depends_on = [
    aws_opensearchserverless_security_policy.encryption,
    aws_opensearchserverless_security_policy.network,
    aws_opensearchserverless_access_policy.bedrock_kb,
  ]
}
