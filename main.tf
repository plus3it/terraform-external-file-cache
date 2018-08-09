data "external" "this" {
  count = "${length(var.uris)}"

  program = "${concat(var.python_cmd, list("${path.module}/file_cache.py"))}"

  query = {
    uri     = "${element(var.uris, count.index)}"
    path    = "${var.cache_dir}/${sha256(element(var.uris, count.index))}"
    refresh = "${var.refresh}"
  }
}
