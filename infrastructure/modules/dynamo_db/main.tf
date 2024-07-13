resource "aws_dynamodb_table" "pharma_tracker_table" {
  name           = var.table_name
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_sub"

  attribute {
    name = "user_sub"
    type = "S"
  }

  attribute {
    name = "name"
    type = "S"
  }

  attribute {
    name = "type"
    type = "S"
  }

  attribute {
    name = "quantity"
    type = "N"  
  }

  # Global Secondary Index (GSI)
  global_secondary_index {
    name               = "name-index"
    hash_key           = "name"
    projection_type    = "ALL"  
  }

  global_secondary_index {
    name               = "type-index"
    hash_key           = "type"
    projection_type    = "ALL"
  }

  global_secondary_index {
    name               = "quantity-index"
    hash_key           = "quantity"
    projection_type    = "ALL"
  }

  tags = {
    Project = var.tag
  }
}
