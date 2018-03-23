# -*- coding: utf-8 -*-
"""Wraps py_getter with a terraform external interface."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import json
import sys

import py_getter
import tf_external


def main(**kwargs):
    return py_getter.main(**kwargs)


if __name__ == "__main__":
    tfe = tf_external.TfExternal()
    args = tfe.query_args(sys.stdin)
    sys.exit(tfe.out_json(main(**args)))
