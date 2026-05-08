# ---------------------------------------------------------------------------
# HTTP API — exposes the query Lambda with a single POST /query route.
# CORS is configured at the API level so the browser frontend can call it
# directly without a proxy.
# ---------------------------------------------------------------------------

resource "aws_apigatewayv2_api" "query" {
  name          = "${var.environment}-vandermeer-query-api"
  protocol_type = "HTTP"
  description   = "Vandermeer and Associates document query endpoint"

  # CORS is intentionally handled inside each Lambda rather than here.
  # AWS API Gateway rejects "null" as an AllowOrigin value, so the built-in
  # CORS config cannot cover file:// requests (which send Origin: null).
  # Routing OPTIONS to the Lambda gives full control over the response headers
  # for every origin, including null.
}

resource "aws_apigatewayv2_integration" "query_lambda" {
  api_id                 = aws_apigatewayv2_api.query.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.rag_query.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "query" {
  api_id    = aws_apigatewayv2_api.query.id
  route_key = "POST /query"
  target    = "integrations/${aws_apigatewayv2_integration.query_lambda.id}"
}

# OPTIONS preflight for /query — browser sends this before every cross-origin POST
resource "aws_apigatewayv2_route" "query_options" {
  api_id    = aws_apigatewayv2_api.query.id
  route_key = "OPTIONS /query"
  target    = "integrations/${aws_apigatewayv2_integration.query_lambda.id}"
}

# $default stage with auto_deploy means changes are live immediately.
# The invoke URL has no stage prefix: https://{id}.execute-api.{region}.amazonaws.com
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.query.id
  name        = "$default"
  auto_deploy = true
}

# Allow API Gateway to invoke the query Lambda
resource "aws_lambda_permission" "apigw_query" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rag_query.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.query.execution_arn}/*/*"
}

# ---------------------------------------------------------------------------
# POST /upload route — proxies to the presign Lambda which returns a
# pre-signed S3 PUT URL. The browser then PUTs the file directly to S3,
# avoiding routing binary payloads through API Gateway.
# ---------------------------------------------------------------------------

resource "aws_apigatewayv2_integration" "presign_lambda" {
  api_id                 = aws_apigatewayv2_api.query.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.presign.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "upload" {
  api_id    = aws_apigatewayv2_api.query.id
  route_key = "POST /upload"
  target    = "integrations/${aws_apigatewayv2_integration.presign_lambda.id}"
}

# OPTIONS preflight for /upload — browser sends this before the presign request
resource "aws_apigatewayv2_route" "upload_options" {
  api_id    = aws_apigatewayv2_api.query.id
  route_key = "OPTIONS /upload"
  target    = "integrations/${aws_apigatewayv2_integration.presign_lambda.id}"
}

# Allow API Gateway to invoke the presign Lambda
resource "aws_lambda_permission" "apigw_presign" {
  statement_id  = "AllowAPIGatewayInvokePresign"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.presign.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.query.execution_arn}/*/*"
}
