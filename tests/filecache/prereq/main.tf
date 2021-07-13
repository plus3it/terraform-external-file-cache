resource "aws_s3_bucket" "this" {
  bucket_prefix = "terraform-external-file-cache-"
}

resource "aws_s3_bucket_object" "this" {
  bucket  = aws_s3_bucket.this.id
  key     = "test.txt"
  content = "TESTING"
}

output "bucket" {
  value = aws_s3_bucket.this
}

output "bucket_object" {
  value = aws_s3_bucket_object.this
}
