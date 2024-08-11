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
  repo_name = "pharmatracker-${var.env}"
  tag       = var.tag
}

module "ecs_sg" {
  source  = "./modules/ecs_sg"
  sg_name = "ecs-sg-pharmatracker-${var.env}"
  vpc_id  = var.vpc_id
  tag     = var.tag
}

module "ecs_cluster" {
  source       = "./modules/ecs_cluster"
  cluster_name = "pharmatracker-${var.env}"
  tag          = var.tag
}