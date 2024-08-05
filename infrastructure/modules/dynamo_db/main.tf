resource "aws_dynamodb_table" "pharma_tracker_table" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_sub"
  range_key    = "medicine_id"

  attribute {
    name = "user_sub"
    type = "S"
  }
  attribute {
    name = "medicine_id"
    type = "S"
  }

  tags = {
    Project = var.tag
  }
}
