resource "aws_iam_user" "user" {
  name = local.project_name
  tags = aws_servicecatalogappregistry_application.app.application_tag
}

resource "aws_iam_user_policy" "ses_send_mail" {
  name = "SesSendMail${local.policy_suffix}"
  user = aws_iam_user.user.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "ses:SendEmail"
      Resource = aws_ses_email_identity.email.arn
    }]
  })
}
