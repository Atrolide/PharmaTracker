# Terraform commands

## Initialize the backend:

terraform init -backend-config=environment/public/dev/backend/backend_config_dev.tfvars

## Reconifgure(swap) the backend

terraform init -reconfigure -backend-config=environment/public/dev/backend/backend_config_dev.tfvars

## Plan/apply changes

terraform plan -var-file=environment/public/dev/variables/variables_dev.tfvars

terraform apply -var-file=environment/public/dev/variables/variables_dev.tfvars

