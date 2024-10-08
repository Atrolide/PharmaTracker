module "pharma_tracker_pool" {
  source              = "./modules/cognito_user_pool"
  pool_name           = "PharmaTrackerPool-${var.env}"
  minimum_length      = local.is_dev ? 6 : 8 # equals 6 if is_dev = true
  require_lowercase   = !local.is_dev        # equals false if is_dev = true
  require_numbers     = !local.is_dev
  require_symbols     = !local.is_dev
  require_uppercase   = !local.is_dev
  cognito_domain_name = var.cognito_domain_name
  tag                 = var.tag
}

module "tablets_table" {
  source     = "./modules/dynamo_db"
  table_name = "MedicineTable-${var.env}"
  tag        = var.tag
}

module "pharma_tracker_repo" {
  source    = "./modules/ecr"
  repo_name = local.prefix
  tag       = var.tag
}

module "ecs_sg" {
  source  = "./modules/ecs_sg"
  sg_name = "ecs-sg-${local.prefix}"
  vpc_id  = var.vpc_id
  tag     = var.tag
}

module "ecs_iam" {
  source       = "./modules/ecs_iam"
  project_name = "role-${local.prefix}"
  tag          = var.tag
}

module "ecs_cluster" {
  source             = "./modules/ecs_cluster"
  cluster_name       = "cluster-${local.prefix}"
  task_family        = "task-${local.prefix}"
  image              = local.image
  tag                = var.tag
  execution_role_arn = module.ecs_iam.execution_role_arn
  security_groups    = [module.ecs_sg.ecs_sg_id]
  subnets            = var.subnets
  task_count         = var.task_count
  depends_on         = [module.pharma_tracker_repo, module.ecs_iam, module.ecs_sg, module.tablets_table, module.pharma_tracker_pool]
}
