output "filepaths" {
  description = "Map of uri => cached filepaths"
  value       = { for uri, external in data.external.this : uri => external.result.filepath }
}
