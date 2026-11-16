# Agent Instructions

Before starting any task in this repository:

1. Run `make agents/sync`. It writes the shared Plus3 IT instructions for this repository's tardigrade-ci version to `.agents/plus3it/AGENTS.md`.
2. Read `.agents/plus3it/AGENTS.md` and follow it together with this file. If the sync fails, tell the user, and don't guess the conventions.

These rules always apply, even without the shared instructions:

- Don't push, open pull requests, publish releases, or apply infrastructure changes unless the user asks. List those steps for a person in your final report.
- Don't edit files under `.agents/plus3it/`; they are generated and overwritten by the sync.

@.agents/plus3it/AGENTS.md

## Repository-specific

### Purpose

This Terraform module downloads files from a list of URIs and caches them on the local machine, using an `external` data source that runs a Python script. The main input is `uris`; each file is saved under `cache_dir` (default `.filecache`) in a directory named for the SHA-256 hash of its URI, and is fetched again only if it is missing or `refresh` is `"true"`. The output `filepaths` is a map of each URI to the local path of its cached file.

### Module-specific files

- `file_cache.py` - Script that the `external` data source runs (`python_cmd` plus this path). It reads the query JSON from stdin, calls `py_getter.main`, and prints the result as JSON with a `filepath` key.
- `py_getter/` - Python package that downloads a URI with `urllib`, retries failures with `backoff`, and writes the file to the destination path. `request_handlers.py` adds an `s3://` handler that uses `boto3` and the optional `s3_endpoint_url`. The package also has a command-line entry point (`python -m py_getter`).
- `tf_external/` - Small Python package that reads the `external` query from stdin and prints JSON results.
- `requirements.txt` - Python packages that the scripts need (`backoff`, `boto3`, and `six`). They must be installed in the Python that `python_cmd` runs.
- `Dockerfile` - Image based on tardigrade-ci that installs `requirements.txt`. The tardigrade-ci `docker/run` target, which the shared lint workflow calls, builds this image when it is not already present.

### Deviations from the terraform-module profile

- There is no `CHANGELOG.md`, so skip the changelog step. The version is kept only in `.bumpversion.cfg`, which has no `files` entries, so `make bumpversion/major`, `make bumpversion/minor`, or `make bumpversion/patch` changes only that file. The config sets `commit = True` and `tag = False`, so bumpversion makes a commit and no tag. `.github/workflows/release.yml` runs on a push to `main` or `master` that changes `.bumpversion.cfg`, and on manual dispatch. It calls the shared release workflow with `GH_RELEASES_TOKEN`. The shared release workflow creates a GitHub Release, and its tag, named after `current_version` when it differs from the latest git tag.
- The Makefile sets `TF_VAR_s3_endpoint_url` to `http://$(MOCKSTACK_HOST or localhost):4615`, for the `terraform/pytest` target only. It does this unless `PYTEST_ARGS` contains `--nomock`. `tests/filecache/main.tf` passes this variable to the module, because the Python code uses `boto3` and does not use the Terraform AWS provider settings, so it needs its own endpoint to reach the mock S3 service. In the mockstack container, `MOCKSTACK_HOST` is set. Outside it, the value is `localhost`. With `--nomock`, the variable is not set and the test reads from real AWS with your own credentials.
- There are no Python unit tests. The only tests are the Terraform configurations in `tests/filecache/` (with `tests/filecache/prereq/`, which creates an S3 bucket and object) and `tests/no_uris/`. `tests/filecache/` downloads two public HTTPS files and the S3 object.
