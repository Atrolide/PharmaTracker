locals {
  is_dev = var.env == "dev" ? true : false

  image = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/pharmatracker-${var.env}:${var.version_tag}"
}