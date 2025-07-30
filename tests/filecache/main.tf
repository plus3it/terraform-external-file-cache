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

  s3_endpoint_url = var.s3_endpoint_url
}

locals {
  uris = [
    "https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm",
    "https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm",
    "s3://${data.terraform_remote_state.prereq.outputs.bucket_object.id}"
  ]
}

output "filepaths" {
  description = "List of cached filepaths retrieved from URIs"
  value       = module.file_cache.filepaths
}

variable "s3_endpoint_url" {
  type        = string
  description = "S3 API endpoint for non-AWS hosts; format: https://hostname:port"
  default     = null
}
