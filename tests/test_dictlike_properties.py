#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from schemadict import schemadict


TEST_SCHEMA = schemadict({
    'name': {
        'type': str,
        'min_len': 3,
        'max_len': 12,
    },
    'age': {
        'type': int,
        '>=': 0,
        '<': 120,
    },
    'has_cat': {
        'type': bool
    }
})


def test_len():
    assert len(TEST_SCHEMA) == 3


def test_iter():
    for k, v in TEST_SCHEMA.items():
        assert isinstance(k, str)
        assert isinstance(v, dict)


def test_repr_str():
    schema = schemadict({'a': {'type': bool}})
    assert repr(schema) == "schemadict({'a': {'type': <class 'bool'>}})"
    assert str(schema) == "{'a': {'type': <class 'bool'>}}"


def test_del():
    schema = schemadict({'a': {'type': bool}, 'b': {'type': int}})
    assert len(schema) == 2

    del schema['b']
    assert len(schema) == 1
    assert schema.get('a', None) is not None
    assert schema.get('b', None) is None
