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

