resource "aws_cognito_user_pool" "pharma_tracker_pool" {
  name = var.pool_name

  username_attributes = ["email"]

  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  verification_message_template {
    default_email_option  = "CONFIRM_WITH_LINK"
    email_message_by_link = "Please click the following link to verify your email address: {##Click Here##}"
    email_subject_by_link = "Verify your email for PharmaTracker"
  }
  password_policy {
    minimum_length    = var.minimum_length
    require_lowercase = var.require_lowercase
    require_numbers   = var.require_numbers
    require_symbols   = var.require_symbols
    require_uppercase = var.require_uppercase
    temporary_password_validity_days = var.temporary_password_validity_days
  }
}

resource "aws_cognito_user_group" "users" {
  name         = "users"
  user_pool_id = aws_cognito_user_pool.pharma_tracker_pool.id

  description = "Group for regular users"
}

resource "aws_cognito_user_group" "admins" {
  name         = "admins"
  user_pool_id = aws_cognito_user_pool.pharma_tracker_pool.id

  description = "Group for administrators"
}

resource "aws_cognito_user_pool_client" "pharma_tracker_pool_client" {
  name            = "${var.pool_name}-client"
  user_pool_id    = aws_cognito_user_pool.pharma_tracker_pool.id
  generate_secret = true
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]

}

resource "aws_cognito_user_pool_domain" "pharma_tracker_pool_domain" {
  domain       = var.cognito_domain_name
  user_pool_id = aws_cognito_user_pool.pharma_tracker_pool.id
}