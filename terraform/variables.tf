variable "default_role" {
  default = "integrations-ci"
}

locals {
  account     = contains(keys(var.accounts), terraform.workspace) ? var.accounts[terraform.workspace] : var.accounts["development"]
  environment = terraform.workspace

  mandatory_moj_tags = {
    business-unit    = "OPG"
    application      = "CasRec-Migration-Mappings"
    account          = local.account.name
    environment-name = terraform.workspace
    is-production    = "false"
    owner            = "opgteam@digital.justice.gov.uk"
  }

  optional_tags = {
    source-code            = "https://github.com/ministryofjustice/opg-data-casrec-migration-mappings"
    infrastructure-support = "opgteam@digital.justice.gov.uk"
  }

  default_tags = merge(local.mandatory_moj_tags, local.optional_tags)
}

variable "accounts" {
  type = map(
    object({
      name       = string
      account_id = string
    })
  )
}
