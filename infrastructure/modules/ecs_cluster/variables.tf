variable "cluster_name" {
  type        = string
  description = "Name of the ECS cluster"
}
variable "task_family" {
  type        = string
  description = "Name of the ECS task family"
}
variable "image" {
  type        = string
  description = "Path to the docker image"
}
variable "execution_role_arn" {
  description = "The ARN of the IAM role that allows ECS tasks to make calls to AWS services"
  type        = string
}
variable "security_groups" {
  type        = list(string)
  description = "List of security groups attached to ECS"
}
variable "subnets" {
  type        = list(string)
  description = "List of security groups attached to ECS"
}
variable "task_count" {
  type        = number
  description = "Desired count of running FARGATE tasks"
}
variable "tag" {
  type = string
}