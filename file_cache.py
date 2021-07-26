# -*- coding: utf-8 -*-
"""Wraps py_getter with a terraform external interface."""
import sys

import py_getter
import tf_external

if __name__ == "__main__":
    tfe = tf_external.TfExternal()
    args = tfe.query_args(sys.stdin)
    sys.exit(tfe.out_json(py_getter.main(**args)))
