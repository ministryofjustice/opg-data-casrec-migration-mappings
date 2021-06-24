terraform {
  backend "s3" {
    bucket         = "opg.terraform.state"
    key            = "opg-data-casrec-migration-mappings/terraform.tfstate"
    encrypt        = true
    region         = "eu-west-1"
    role_arn       = "arn:aws:iam::311462405659:role/integrations-ci"
    dynamodb_table = "remote_lock"
  }
}

provider "aws" {
  region = "eu-west-1"

  assume_role {
    role_arn     = "arn:aws:iam::${local.account.account_id}:role/${var.default_role}"
    session_name = "terraform-session"
  }
}
