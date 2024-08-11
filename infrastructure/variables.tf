variable "region" {
  type        = string
  description = "Region where the resources are deployed to"
}

variable "env" {
  description = "Environment to deploy to"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "prd"], var.env)
    error_message = "Invalid environment specified. Allowed values are 'dev' or 'prd'."
  }
}

variable "cognito_domain_name" {
  type        = string
  description = "Name of the domain for Cognito User Pool."
}

variable "tag" {
  type        = string
  description = "Default resource tag"
  default     = "Thesis"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID for ECS SG"
}