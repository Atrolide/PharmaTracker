output "execution_role_arn" {
  description = "The ARN of the IAM role that allows ECS tasks to make calls to AWS services"
  value       = aws_iam_role.ecs_task_execution_role.arn
}