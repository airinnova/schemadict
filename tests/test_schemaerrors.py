#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from schemadict import schemadict, SchemaError

import pytest


def test_valid_keys():
    """Only allow strings as keys"""

    schemadict({'$required_keys': ['a'], 'a': {'type': bool}})
    with pytest.raises(SchemaError):
        schemadict({1: ['a'], 'a': {'type': bool}})

    schemadict().update({'b': {'type': bool}})
    with pytest.raises(SchemaError):
        schemadict().update({3.14159: {'type': bool}})

    schemadict()['c'] = {'type': int}
    with pytest.raises(SchemaError):
        schemadict()[42] = {'type': int}
