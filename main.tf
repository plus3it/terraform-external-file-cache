data "external" "this" {
  for_each = toset(var.uris)

  program = concat(var.python_cmd, list("${path.module}/file_cache.py"))

  query = {
    uri     = each.key
    path    = "${var.cache_dir}/${sha256(each.key)}"
    refresh = var.refresh
  }
}
