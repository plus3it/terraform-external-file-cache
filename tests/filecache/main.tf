terraform {
  required_version = ">= 0.12"
}

data "terraform_remote_state" "prereq" {
  backend = "local"
  config = {
    path = "prereq/terraform.tfstate"
  }
}

module "file_cache" {
  source = "../../"

  uris    = local.uris
  refresh = true

  s3_endpoint_url = "http://${var.mockstack_host}:${var.mockstack_port}"
}

locals {
  uris = [
    "https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm",
    "https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm",
    "s3://${data.terraform_remote_state.prereq.outputs.bucket.id}/${data.terraform_remote_state.prereq.outputs.bucket_object.id}"
  ]
}

output "filepaths" {
  description = "List of cached filepaths retrieved from URIs"
  value       = module.file_cache.filepaths
}
