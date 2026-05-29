resource "aws_iam_user" "api" {
  name = "${local.project_name}-api"
  path = "/${local.project_name}/"
  tags = aws_servicecatalogappregistry_application.app.application_tag
}

resource "aws_iam_user_policy" "ses" {
  name = "SESSendMail"
  user = aws_iam_user.api.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "ses:SendEmail"
      Resource = aws_ses_email_identity.email.arn
    }]
  })
}

resource "aws_iam_user_policy" "logs" {
  name = "CloudWatchLogs"
  user = aws_iam_user.api.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.log_group.arn}:*"
      },
      {
        Effect   = "Allow"
        Action   = "logs:CreateLogGroup"
        Resource = aws_cloudwatch_log_group.log_group.arn
      }
    ]
  })
}
