output "ecs_sg_id" {
  description = "The ARN of the IAM role that allows ECS tasks to make calls to AWS services"
  value       = aws_security_group.ecs_sg.id
}