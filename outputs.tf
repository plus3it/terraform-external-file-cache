output "filepaths" {
  description = "List of cached filepaths"
  value       = ["${data.external.this.*.result.filepath}"]
}
