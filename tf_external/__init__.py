# -*- coding: utf-8 -*-
"""Provides wrapper implementing the terraform external interface."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import json


class TfExternal(object):
    """Wrap Terraform External provider."""

    @staticmethod
    def query_args(obj):
        """Load json object from stdin."""
        return {} if obj.isatty() else json.load(obj)

    @staticmethod
    def out_json(result):
        """Print result to stdout."""
        print(json.dumps(result))
