variable "region" {
  type        = string
  description = "Region where the resources are deployed to"
}

variable "env" {
  description = "Environment to deploy to"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "tud", "prd"], var.env)
    error_message = "Invalid environment specified. Allowed values are 'dev', 'tud', or 'prd'."
  }
}

variable "cognito_domain_name" {
  type        = string
  description = "Name of the domain for Cognito User Pool."
}
