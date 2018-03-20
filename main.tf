data "external" "this" {
  count = "${length(var.uris)}"

  program = ["python", "${path.module}/py_getter", "--json", "-"]

  query = {
    uri     = "${element(var.uris, count.index)}"
    path    = "${path.module}/.cache/${sha256(element(var.uris, count.index))}"
    refresh = "${var.refresh}"
  }
}
