output "bucket_name" {
  value = aws_s3_bucket.costkiller_reports.bucket
}

output "lambda_name" {
  value = aws_lambda_function.costkiller.function_name
}
