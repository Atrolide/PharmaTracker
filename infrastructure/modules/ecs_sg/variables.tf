variable "vpc_id" {
  type        = string
  description = "VPC ID for ECS SG"
}
variable "sg_name" {
  type        = string
  description = "Security Group name for ECS"
}
variable "tag" {
  type = string
}