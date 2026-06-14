resource "aws_cloudwatch_log_group" "log_group" {
  name              = local.project_name
  retention_in_days = 14
  tags              = aws_servicecatalogappregistry_application.app.application_tag
}
