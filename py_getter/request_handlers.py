# -*- coding: utf-8 -*-
"""Extends urllib with additional handlers."""
import io
from email import message_from_string

import boto3

from six.moves import urllib


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
        origurl = f"s3://{bucket_name}/{key_name}"

        if key is None:
            raise urllib.error.URLError(f"no such resource: {origurl}")

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
                f"{header}: {value}" for header, value in headers if value is not None
            )
        )

        return urllib.response.addinfourl(BufferedIOS3Key(key), headers, origurl)
