# File for supplying variables

task_count          = "DESIRED-TASK-COUNT"  # Specify the number of Fargate Tasks, e.g., 1
region              = "YOUR-AWS-REGION"     # Specify your AWS region here, e.g., us-east-1
env                 = "YOUR-STAGING-ENV"    # Environment can be either "dev", "tud" or "prd". 
cognito_domain_name = "YOUR-COGNITO-DOMAIN" # Domain names must follow this format: ^[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?$
vpc_id              = "YOUR-VPC-ID"
account_id          = "YOU-AWS-ACCOUNT-ID"
version_tag         = "YOUR-IMAGE-TAG"      # Specify an image tag, e.g., "latest"
subnets = [
  "YOUR-SUBNET-ID"
]
