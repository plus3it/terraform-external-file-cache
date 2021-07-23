variable "cache_dir" {
  type        = string
  description = "Path where files will be cached"
  default     = ".filecache"
}

variable "uris" {
  type        = list(string)
  description = "List of URIs to the files to be retrieved and cached locally"
  default     = []
}

variable "refresh" {
  type        = string
  description = "Retrieve file even if the URI is already cached on the system"
  default     = "false"
}

variable "python_cmd" {
  type        = list(string)
  description = "Command to use when executing the python external resource"
  default     = ["python"]
}

variable "s3_endpoint_url" {
  type        = string
  description = "S3 API endpoint for non-AWS hosts; format: https://hostname:port"
  default     = null
}
