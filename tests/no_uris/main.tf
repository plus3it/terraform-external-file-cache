module "file_cache" {
  source = "../../"

  s3_endpoint_url = "http://${var.mockstack_host}:${var.mockstack_port}"
}

output "filepaths" {
  description = "List of cached filepaths retrieved from URIs"
  value       = module.file_cache.filepaths
}
