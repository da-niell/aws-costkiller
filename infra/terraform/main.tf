provider "aws" {
  region = var.aws_region
}

resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "costkiller_reports" {
  bucket        = "costkiller-reports-${random_id.suffix.hex}"
  force_destroy = true
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "costkiller_lambda_exec_${random_id.suffix.hex}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
      Effect = "Allow",
      Sid    = ""
    }]
  })
}

resource "aws_iam_role_policy" "costkiller_lambda_inline_policy" {
  name = "costkiller_lambda_policy"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeVolumes",
          "s3:ListAllMyBuckets",
          "s3:ListBucket",
          "s3:ListBucketVersions",
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:PutObject",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = "s3:PutObject",
        Resource = "${aws_s3_bucket.costkiller_reports.arn}/*"
      }
    ]
  })
}

resource "aws_lambda_function" "costkiller" {
  function_name = "costkiller-scan"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.9"
  timeout       = 60
  memory_size   = 256
  filename      = "${path.module}/lambda/costkiller.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda/costkiller.zip")

  environment {
    variables = {
      REPORT_BUCKET = aws_s3_bucket.costkiller_reports.bucket
    }
  }
}

resource "aws_cloudwatch_event_rule" "daily_trigger" {
  name                = "costkiller-daily-trigger"
  description         = "Trigger Lambda daily at 8 AM UTC"
  schedule_expression = "cron(0 8 * * ? *)"
}

resource "aws_cloudwatch_event_target" "invoke_lambda" {
  rule      = aws_cloudwatch_event_rule.daily_trigger.name
  target_id = "CostKillerLambda"
  arn       = aws_lambda_function.costkiller.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.costkiller.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_trigger.arn
}
