resource "aws_dynamodb_table" "pharma_tracker_table" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_sub"

  attribute {
    name = "user_sub"
    type = "S"
  }

  tags = {
    Project = var.tag
  }
}
