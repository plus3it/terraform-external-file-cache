[![License](https://img.shields.io/github/license/plus3it/terraform-external-file-cache.svg)](LICENSE)
[![Travis CI Build Status](https://travis-ci.org/plus3it/terraform-external-file-cache.svg?branch=master)](https://travis-ci.org/plus3it/terraform-external-file-cache)
[![pullreminders](https://pullreminders.com/badge.svg)](https://pullreminders.com?ref=badge)

# terraform-external-file-cache
Terraform module to retrieve and cache files. This module retrieves files from
a list of URIs and caches them on the local system. If a file already exists in
the cache, it is not retrieved again. To force retrieval, use `refresh = true`.

The module uses an external data resource because the Terraform HTTP provider
can only retrieve `text/*` or `application/json` content types. It does not
support arbitrary files.

## Usage

```
module "file_cache" {
  source = "git::https://github.com/plus3it/terraform-external-file-cache"

  uris = [
    "https://url/to/some/file1",
    "s3://somebucket/some/file2",
    "file:///some/local/file3",
  ]

  refresh = "false"
}
```

## Examples

*   [Retrieve files and push them to S3 bucket][s3]
*   [Retrieve files and provision them in an ec2 instance][ec2]

[s3]: https://github.com/plus3it/terraform-external-file-cache/tree/master/examples/s3
[ec2]: https://github.com/plus3it/terraform-external-file-cache/tree/master/examples/ec2

## Requirements

This module uses an `external` data resource based on a custom python library
to retrieve the files, [`py_getter`](py_getter). You must have python installed
and in the PATH to use this Terraform module. The `py_getter` library also
requires the packages in the [`requirements.txt`](requirements.txt) file.
Install them using `pip`:

```
sudo pip install -r requirements.txt
```

If you do not have admin/root privileges to install packages, you can either
install packages into the user space (and make sure pip's user environment is
in your PATH):

```
pip install --user -r requirements.txt
```

Or you can use pipenv with the `python_cmd` variable to install packages into
a virtualenv:

```
pip install --user pipenv  # or on macos `brew install pipenv`
pipenv install -r requirements.txt
terraform apply -var python_cmd='["pipenv","run","python"]' ...
```

## Limitations

When retrieving files from an S3 bucket this module will resolve the credential
based on the [`boto3` credential resolution order][boto3-credential]. However,
only the ENV, config file, and instance role mechanisms are supported by this
module (i.e. cannot pass access/secret/session keys through the module).

This module **will not** use any credential explicitly specified in a Terraform
`aws` provider, as the `external` data resource is not (understandably)
integrated with the `aws` provider.

[boto3-credential]: http://boto3.readthedocs.io/en/latest/guide/configuration.html#configuring-credentials

## Supported URI Protocols

The custom `py_getter` library is based on `urllib`, so this Terraform module
supports any URI protocol that is understood by a `urllib` handler, including
`http://`, `https://`, `ftp://`, `file://`, etc. See the [`urllib`][urllib]
docs for details on built-in handlers.

The module also includes a custom handler for S3 URIs, `s3://`.

[urllib]: https://docs.python.org/3/library/urllib.request.html

## Testing

Manual testing:

```
# Replace "xxx" with an actual AWS profile, then execute the integration tests.
export AWS_PROFILE=xxx 
make terraform/pytest PYTEST_ARGS="-v --nomock"
```

For automated testing, PYTEST_ARGS is optional and no profile is needed:

```
make mockstack/up
make terraform/pytest PYTEST_ARGS="-v"
make mockstack/clean
```

<!-- BEGIN TFDOCS -->
## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_external"></a> [external](#provider\_external) | n/a |

## Resources

| Name | Type |
|------|------|
| [external_external.this](https://registry.terraform.io/providers/hashicorp/external/latest/docs/data-sources/external) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_cache_dir"></a> [cache\_dir](#input\_cache\_dir) | Path where files will be cached | `string` | `".filecache"` | no |
| <a name="input_python_cmd"></a> [python\_cmd](#input\_python\_cmd) | Command to use when executing the python external resource | `list(string)` | <pre>[<br>  "python"<br>]</pre> | no |
| <a name="input_refresh"></a> [refresh](#input\_refresh) | Retrieve file even if the URI is already cached on the system | `string` | `"false"` | no |
| <a name="input_s3_endpoint_url"></a> [s3\_endpoint\_url](#input\_s3\_endpoint\_url) | S3 API endpoint for non-AWS hosts; format: https://hostname:port | `string` | `null` | no |
| <a name="input_uris"></a> [uris](#input\_uris) | List of URIs to the files to be retrieved and cached locally | `list(string)` | `[]` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_filepaths"></a> [filepaths](#output\_filepaths) | Map of uri => cached filepaths |

<!-- END TFDOCS -->

## Authors

This module is managed by [Plus3 IT Systems](https://github.com/plus3it).

## License

Apache 2 licensed. See [LICENSE](LICENSE.md) for details.
