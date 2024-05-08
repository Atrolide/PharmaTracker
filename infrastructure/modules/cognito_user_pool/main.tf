resource "aws_cognito_user_pool" "pharma_tracker_pool" {
  name = var.pool_name

  password_policy {
    minimum_length    = var.minimum_length
    require_lowercase = var.require_lowercase
    require_numbers   = var.require_numbers
    require_symbols   = var.require_symbols
    require_uppercase = var.require_uppercase
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
