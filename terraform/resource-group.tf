resource "aws_resourcegroups_group" "rg" {
  name = local.project_name
  resource_query {
    type = "TAG_FILTERS_1_0"
    query = jsonencode({
      ResourceTypeFilters = ["AWS::AllSupported"]
      TagFilters = [
        {
          Key    = "awsApplication"
          Values = [aws_servicecatalogappregistry_application.app.application_tag["awsApplication"]]
        }
      ]
    })
  }
  tags = aws_servicecatalogappregistry_application.app.application_tag
}
