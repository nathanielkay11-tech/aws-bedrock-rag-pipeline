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

resource "aws_opensearchserverless_collection" "kb" {
  name = local.collection_name
  type = "VECTORSEARCH"

  depends_on = [
    aws_opensearchserverless_security_policy.encryption,
    aws_opensearchserverless_security_policy.network,
    aws_opensearchserverless_access_policy.bedrock_kb,
  ]
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
      Principal = [
        aws_iam_role.bedrock_kb.arn,
        "arn:aws:iam::251478237846:user/terraform-learn-user",
      ]
    }
  ])
}

# Collection dev-legal-kb (u0hp7ktjncq6c4w9ejqg) exists and is ACTIVE.
# It is intentionally unmanaged by Terraform because aoss:ListTagsForResource
# is not granted on this deployment user. The ARN is stored in local.collection_arn.
# To re-import: terraform import aws_opensearchserverless_collection.kb u0hp7ktjncq6c4w9ejqg
