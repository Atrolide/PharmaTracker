resource "aws_ecr_repository" "pharma_tracker_repo" {
  name = var.repo_name

  image_scanning_configuration {
    scan_on_push = true
  }

  image_tag_mutability = "MUTABLE"

  tags = {
    Project = var.tag
  }
}
