# -*- coding: utf-8 -*-
"""Downloads files using urllib.request.urlopen, with additional handlers."""
import argparse
import io
import os
import shutil
import ssl
import sys

import backoff
import botocore
from six.moves import urllib

from py_getter import request_handlers

URLOPEN_RETRY_EXCEPTIONS = (urllib.error.URLError,)

GETTER_RETRY_EXCEPTIONS = (
    botocore.exceptions.ReadTimeoutError,
    botocore.exceptions.MetadataRetrievalError,
)


HANDLER = request_handlers.S3Handler()
urllib.request.install_opener(urllib.request.build_opener(HANDLER))


def basename_from_uri(uri):
    """Return the basename/filename/leaf part of a URI."""
    return os.path.basename(urllib.parse.urlparse(uri).path)


def qualify_uri(uri):
    """Return a URI compatible with urllib, handling relative file:// URIs."""
    parts = urllib.parse.urlparse(uri)
    scheme = parts.scheme

    if scheme != "file":
        # Return non-file paths unchanged
        return uri

    # Expand relative file paths and convert them to uri-style
    path = urllib.request.pathname2url(
        os.path.abspath(
            os.path.expanduser("".join([x for x in [parts.netloc, parts.path] if x]))
        )
    )

    return urllib.parse.urlunparse((scheme, "", path, "", "", ""))


def qualify_path(path):
    """Qualify the destination path."""
    return os.path.relpath(os.path.expanduser(path))


def qualify_filename(filename):
    """Qualify the destination filename."""
    return urllib.parse.unquote(filename)


def create_path(path):
    """Create the destination directory."""
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


def to_bool(data):
    """Convert truthy strings to boolean."""
    return str(data).lower() == "true"


@backoff.on_exception(backoff.expo, URLOPEN_RETRY_EXCEPTIONS, max_tries=5)
def urlopen_retry(uri):
    """Retry urlopen on exception."""
    kwargs = {}
    try:
        # trust the system's default CA certificates
        # proper way for 2.7.9+ on Linux
        if uri.startswith("https://"):
            kwargs["context"] = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    except AttributeError:
        pass

    # pylint: disable=consider-using-with
    return urllib.request.urlopen(uri, **kwargs)


@backoff.on_exception(backoff.expo, GETTER_RETRY_EXCEPTIONS, max_tries=5)
def getter(request, dest):
    """Retrieve a file and saves it to the local filesystem."""
    with io.open(dest, mode="wb") as handle:
        shutil.copyfileobj(request, handle)


def main(uri, path, refresh=False, s3_endpoint_url=None):
    """Coordinate the retrieval of a file from a URI."""
    HANDLER.connect(s3_endpoint_url=s3_endpoint_url)

    qualified_path = qualify_path(path)
    qualified_dest = os.path.join(
        qualified_path, qualify_filename(basename_from_uri(uri))
    )
    create_path(qualified_path)
    if not os.path.isfile(qualified_dest) or to_bool(refresh):
        getter(urlopen_retry(qualify_uri(uri)), qualified_dest)
    return {"filepath": qualified_dest}


def cli():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(prog="py-getter")
    parser.add_argument("URI")
    parser.add_argument("PATH")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--s3-endpoint-url")

    args = parser.parse_args()

    sys.exit(main(args.URI, args.PATH, args.refresh, args.s3_endpoint_url))
