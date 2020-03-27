terraform {
  required_version = ">= 0.12"
}


module "file_cache" {
  source = "../../"
}

output "filepaths" {
  description = "List of cached filepaths retrieved from URIs"
  value       = module.file_cache.filepaths
}
