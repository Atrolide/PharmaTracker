# Cognito User Pool module variables

variable "pool_name" {
  type        = string
  description = "Name of the Cognito User Pool"
}

variable "minimum_length" {
  type        = number
  description = "Minimum length of the password"
}

variable "require_lowercase" {
  type = bool
}

variable "require_numbers" {
  type = bool
}

variable "require_symbols" {
  type = bool
}

variable "require_uppercase" {
  type = bool
}

variable "cognito_domain_name" {
  type = string
}

variable "temporary_password_validity_days" {
  type    = number
  default = 7
}

variable "tag" {
  type = string
}