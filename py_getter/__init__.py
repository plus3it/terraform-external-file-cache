# -*- coding: utf-8 -*-
"""Downloads files using urllib.request.urlopen, with additional handlers."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import argparse
import io
import os
import shutil
import sys

from six.moves.urllib import parse, request

from py_getter import request_handlers


request.install_opener(request.build_opener(request_handlers.S3Handler))


def basename_from_uri(uri):
    """Return the basename/filename/leaf part of a URI."""
    return os.path.basename(parse.urlparse(uri).path)


def qualify_uri(uri):
    """Return a URI compatible with urllib, handling relative file:// URIs."""
    parts = parse.urlparse(uri)
    scheme = parts.scheme

    if scheme != 'file':
        # Return non-file paths unchanged
        return uri

    # Expand relative file paths and convert them to uri-style
    path = request.pathname2url(os.path.abspath(os.path.expanduser(
        ''.join([x for x in [parts.netloc, parts.path] if x]))))

    return parse.urlunparse((scheme, '', path, '', '', ''))


def qualify_path(path):
    """Qualify the destination path."""
    return os.path.abspath(os.path.expanduser(path))


def qualify_filename(filename):
    """Qualify the destination filename."""
    return parse.unquote(filename)


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


def getter(uri, dest):
    """Retrieve a file and saves it to the local filesystem."""
    response = request.urlopen(uri)
    with io.open(dest, mode="wb") as handle:
        shutil.copyfileobj(response, handle)


def main(uri, path, refresh=False):
    """Coordinate the retrieval of a file from a URI."""
    qualified_path = qualify_path(path)
    qualified_dest = os.path.join(
        qualified_path, qualify_filename(basename_from_uri(uri))
    )
    create_path(qualified_path)
    if not os.path.isfile(qualified_dest) or to_bool(refresh):
        getter(qualify_uri(uri), qualified_dest)
    return {"filepath": qualified_dest}


def cli():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(prog="py-getter")
    parser.add_argument("URI")
    parser.add_argument("PATH")
    parser.add_argument("--refresh", action="store_true")

    args = parser.parse_args()

    sys.exit(main(args.URI, args.PATH, args.refresh))
