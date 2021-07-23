# -*- coding: utf-8 -*-
"""Extends urllib with additional handlers."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import io
import os
from email import message_from_string

import boto3
import localstack_client.session

from six.moves import urllib

AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", default="us-east-1")


class BufferedIOS3Key(io.BufferedIOBase):
    """Add a read method to S3 key object."""

    def __init__(self, key, *args, **kwargs):
        """Read key."""
        # pylint: disable=super-with-arguments
        super(BufferedIOS3Key, self).__init__(*args, **kwargs)
        self.read = key.get()["Body"].read


class S3Handler(urllib.request.BaseHandler):
    """Define urllib handler for S3 objects."""

    def __init__(self):
        """Initiate S3 resource connection."""
        super().__init__()
        self.s3_conn = None

    def connect(self, s3_endpoint_url=None):
        """Use AWS or a mock stack for API calls."""
        if s3_endpoint_url and (
            "localhost" in s3_endpoint_url or "localstack" in s3_endpoint_url
        ):
            localstack_session = localstack_client.session.Session(
                localstack_host=s3_endpoint_url
            )
            self.s3_conn = localstack_session.resource(
                "s3", region_name=AWS_DEFAULT_REGION
            )
        else:
            session = boto3.Session()
            self.s3_conn = session.resource("s3", endpoint_url=s3_endpoint_url)

    def s3_open(self, req):
        """Open S3 objects."""
        # Credit: <https://github.com/ActiveState/code/tree/master/recipes/Python/578957_Urllib_handler_AmazS3>  # noqa: E501, pylint: disable=line-too-long

        # The implementation was inspired mainly by the code behind
        # urllib.request.FileHandler.file_open().

        try:
            # py3 urllib
            selector = req.selector
        except AttributeError:
            # py2 urllib2
            selector = req.get_selector()

        bucket_name = req.host
        key_name = selector[1:]

        if not bucket_name or not key_name:
            raise urllib.error.URLError("url must be in the format s3://<bucket>/<key>")

        key = self.s3_conn.Object(bucket_name=bucket_name, key=key_name)
        origurl = "s3://{0}/{1}".format(bucket_name, key_name)

        if key is None:
            raise urllib.error.URLError("no such resource: {0}".format(origurl))

        headers = [
            ("Content-type", key.content_type),
            ("Content-encoding", key.content_encoding),
            ("Content-language", key.content_language),
            ("Content-length", key.content_length),
            ("Etag", key.e_tag),
            ("Last-modified", key.last_modified),
        ]

        headers = message_from_string(
            "\n".join(
                "{0}: {1}".format(header, value)
                for header, value in headers
                if value is not None
            )
        )

        return urllib.response.addinfourl(BufferedIOS3Key(key), headers, origurl)
