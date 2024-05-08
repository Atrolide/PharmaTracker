module "pharma_tracker_pool" {
  source            = "./modules/cognito_user_pool"
  pool_name         = "PharmaTrackerPool"
  minimum_length    = 8
  require_lowercase = true
  require_numbers   = true
  require_symbols   = true
  require_uppercase = true
}