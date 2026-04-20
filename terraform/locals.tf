locals {
  project_name  = "zapis-stavy"
  policy_suffix = join("", [for part in split("-", local.project_name) : title(part)])
}
