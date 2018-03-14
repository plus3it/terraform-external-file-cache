locals {
  uri_map = {
    "https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm" = "epel/7/"
    "https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm" = "epel/6/"
  }

  uris     = "${keys(local.uri_map)}"
  s3_paths = "${values(local.uri_map)}"
}

module "file_cache" {
  source = "../../"

  uris = "${local.uris}"
}

resource "aws_s3_bucket" "example" {
  bucket_prefix = "terraform-external-file-cache-"
}

resource "aws_s3_bucket_object" "example" {
  count = "${length(local.uris)}"

  bucket = "${aws_s3_bucket.example.id}"
  key    = "${element(local.s3_paths, count.index)}${basename(element(module.file_cache.filepaths, count.index))}"
  source = "${element(module.file_cache.filepaths, count.index)}"
}

output "bucket_name" {
  description = "Name of the S3 Bucket"
  value       = "${aws_s3_bucket.example.id}"
}

output "keys" {
  description = "List of keys created in the S3 bucket"
  value       = ["${aws_s3_bucket_object.example.*.key}"]
}

output "etags" {
  description = "List of ETags generated for each object in the bucket"
  value       = ["${aws_s3_bucket_object.example.*.etag}"]
}

output "filepaths" {
  description = "List of cached filepaths retrieved from URIs"
  value       = ["${module.file_cache.filepaths}"]
}
