variable "uris" {
  type        = "list"
  description = "List of URIs to the files to be retrieved and cached locally"
  default     = []
}

variable "refresh" {
  type        = "string"
  description = "Retrieve file even if the URI is already cached on the system"
  default     = "false"
}
