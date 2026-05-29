resource "aws_iam_role" "gh_action" {
  name = "${local.project_name}-gh-action"
  path = "/${local.project_name}/"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      "Effect" : "Allow",
      "Principal" : {
        "Federated" : "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action" : "sts:AssumeRoleWithWebIdentity",
      "Condition" : {
        "StringEquals" : {
          "token.actions.githubusercontent.com:sub" : "repo:lukinkratas/zapis-stavy-fastapi:ref:refs/heads/main",
          "token.actions.githubusercontent.com:aud" : "sts.amazonaws.com"
        }
      }
    }]
  })
  tags = aws_servicecatalogappregistry_application.app.application_tag
}

resource "aws_iam_role_policy" "s3_tf_state" {
  name = "s3-tf-state"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow",
        Action   = "s3:ListBucket",
        Resource = "arn:aws:s3:::terraform-state-8f45b0ac"
      },
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ],
        Resource = "arn:aws:s3:::terraform-state-8f45b0ac/${local.project_name}/terraform.tfstate"
      },
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ],
        Resource = "arn:aws:s3:::terraform-state-8f45b0ac/${local.project_name}/terraform.tfstate.tflock"
      }
    ]
  })
}

resource "aws_iam_role_policy" "app" {
  name = "app"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "servicecatalog:CreateApplication",
          "servicecatalog:DeleteApplication",
          "servicecatalog:GetApplication",
          "servicecatalog:UpdateApplication",
          "servicecatalog:TagResource",
          "servicecatalog:UntagResource"
        ],
        Resource = aws_servicecatalogappregistry_application.app.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "resource_group" {
  name = "resource-group"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "resource-groups:CreateGroup",
          "resource-groups:DeleteGroup",
          "resource-groups:GetGroup",
          "resource-groups:GetGroupQuery",
          "resource-groups:UpdateGroup",
          "resource-groups:UpdateGroupQuery",
          "resource-groups:Tag",
          "resource-groups:Untag",
          "resource-groups:GetTags",
          "tag:TagResources",
          "tag:UntagResources"
        ],
        Resource = aws_resourcegroups_group.rg.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "ses" {
  name = "ses"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "ses:VerifyEmailIdentity",
        "ses:DeleteIdentity",
        "ses:GetIdentityVerificationAttributes"
      ],
      Resource = aws_ses_email_identity.email.arn
    }]
  })
}

resource "aws_iam_role_policy" "logs" {
  name = "logs"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "logs:CreateLogGroup",
        "logs:DeleteLogGroup",
        "logs:DescribeLogGroups",
        "logs:PutRetentionPolicy",
        "logs:DeleteRetentionPolicy",
        "logs:ListTagsForResource",
        "logs:TagResource",
        "logs:UntagResource"
      ],
      Resource = aws_cloudwatch_log_group.log_group.arn
    }]
  })
}

resource "aws_iam_role_policy" "iam_self" {
  name = "iam-self"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = "iam:CreateRole"
        Resource = "arn:aws:iam::*:role/${local.project_name}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "iam:GetRole",
          "iam:GetRolePolicy",
          "iam:ListAttachedRolePolicies",
          "iam:ListRolePolicies",
        ]
        Resource = aws_iam_role.gh_action.arn
      },
      {
        Effect = "Deny"
        Action = [
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:CreatePolicyVersion",
          "iam:SetDefaultPolicyVersion",
        ]
        Resource = aws_iam_role.gh_action.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "iam_api_user" {
  name = "iam-api-user"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = "iam:CreateUser"
        Resource = "arn:aws:iam::*:user/${local.project_name}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "iam:GetUser",
          "iam:DeleteUser",
          "iam:AttachUserPolicy",
          "iam:DetachUserPolicy",
          "iam:ListAttachedUserPolicies",
          "iam:CreateAccessKey",
          "iam:DeleteAccessKey",
          "iam:ListAccessKeys",
          "iam:TagUser",
          "iam:UntagUser",
        ]
        Resource = aws_iam_user.api.arn
      }
    ]
  })
}
