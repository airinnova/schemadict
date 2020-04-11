#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from schemadict import schemadict

import pytest


def test_type_bool():
    """Test type bool"""

    schema = schemadict({
        '$required_keys': ['job_done'],
        'job_done': {'type': bool}
    })

    schema.validate({'job_done': True})
    schema.validate({'job_done': True, 'some_other_key': 'value_is_ignored'})

    with pytest.raises(TypeError):
        schema.validate({'job_done': 100})

    with pytest.raises(KeyError):
        schema.validate({'required_key_is_missing': True})


def _check_numerical_ge_le(num_type, ge, le):
    schema = schemadict({
        '$required_keys': ['myNumber'],
        'myNumber': {'type': num_type, '>=': ge, '<=': le}
    })

    diff = le - ge
    n = ge + 0.1*diff
    if num_type in (int, float):
        n = num_type(n)

    # Expected to pass...
    schema.validate({'myNumber': ge})
    schema.validate({'myNumber': le})
    schema.validate({'myNumber': n})
    schema.validate({'myNumber': n, 'some_other_key': 'value_is_ignored'})

    with pytest.raises(ValueError):
        schema.validate({'myNumber': ge-1})  # Number too small

    with pytest.raises(ValueError):
        schema.validate({'myNumber': le+1})  # Number too large

    with pytest.raises(TypeError):
        schema.validate({'myNumber': str(n)})

    with pytest.raises(KeyError):
        schema.validate({'required_key_is_missing': True})


def _check_numerical_gt_lt(num_type, gt, lt):
    schema = schemadict({
        '$required_keys': ['myNumber'],
        'myNumber': {'type': num_type, '>': gt, '<': lt}
    })

    diff = lt - gt
    n = gt + 0.1*diff
    if num_type in (int, float):
        n = num_type(n)

    # Expected to pass...
    schema.validate({'myNumber': n})
    schema.validate({'myNumber': n, 'some_other_key': 'value_is_ignored'})

    with pytest.raises(ValueError):
        schema.validate({'myNumber': gt})  # Number too small

    with pytest.raises(ValueError):
        schema.validate({'myNumber': lt})  # Number too large

    with pytest.raises(TypeError):
        schema.validate({'myNumber': str(n)})

    with pytest.raises(KeyError):
        schema.validate({'required_key_is_missing': True})


def test_type_int():
    """Test type int"""
    _check_numerical_ge_le(int, -100, 100)
    _check_numerical_gt_lt(int, -100, 100)


def test_type_float():
    """Test type float"""
    _check_numerical_ge_le(float, -3.3343, 55.34)
    _check_numerical_gt_lt(float, -3.3343, 55.34)


def test_type_str():
    """Test type str"""

    schema = schemadict({
        '$required_keys': ['firstname', 'lastname'],
        'firstname': {'type': str, 'min_len': 1, 'max_len': 10},
        'lastname': {'type': str},
    })

    schema.validate({'firstname': 'Neil', 'lastname': 'Armstrong'})
    schema.validate({
        'firstname': 'Homer',
        'lastname': 'Simpson-VeryLongLastNameIsOk',
        'some_other_key': 'value_is_ignored',
    })

    with pytest.raises(TypeError):
        schema.validate({'firstname': 'Bart', 'lastname': True})

    with pytest.raises(KeyError):
        schema.validate({'required_key_is_missing': 'Bart'})

    # Test regex
    schema = schemadict({
        'a': {'type': str, 'regex': r'[a-z]*[0-9]'},
    })
    schema.validate({'a': 'hello1'})
    schema.validate({'a': 'monkey8'})

    with pytest.raises(ValueError):
        schema.validate({'a': 'Monkey8'})  # Uppercase letter not allowed

    with pytest.raises(ValueError):
        schema.validate({'a': 'test'})

    # More regex tests
    schema = schemadict({
        'ip_addrs': {
            'type': list,
            'item_schema': {
                'type': str,
                'regex': r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',
                'min_len': 1,
            },
        },
    })

    # schema.validate({'ip_addrs': ['127.0.0.1', '192.168.1.1']})

def _check_iterables(iterable_type):
    schema = schemadict({
        '$required_keys': ['fruits', 'numbers'],
        'fruits': {'type': iterable_type, 'item_types': str, 'min_len': 1, 'max_len': 3},
        'numbers': {'type': iterable_type, 'item_types': int},
    })

    testdict = {
        'fruits': iterable_type(['papaya', 'avocado', 'melon']),
        'numbers': iterable_type([1, 55, 56, 913]),
    }
    schema.validate(testdict)

    testdict.update({'some_other_key': 'value_is_ignored'})
    schema.validate(testdict)

    testdict['fruits'] = iterable_type(['papaya', True])
    with pytest.raises(TypeError):
        schema.validate(testdict)

    del testdict['fruits']
    with pytest.raises(KeyError):
        schema.validate(testdict)


def test_type_list():
    """Test type list"""
    _check_iterables(list)


def test_type_tuple():
    """Test type tuple"""
    _check_iterables(tuple)


def test_type_dict():
    """Test type dict"""

    pet_schema = schemadict({
        '$required_keys': ['animal'],
        'animal': {'type': str, 'min_len': 0},
        'name': {'type': str, 'min_len': 0},
        'age': {'type': int, '>': 0},
    })

    schema = schemadict({
        '$required_keys': ['name', 'pet'],
        'name': {
            'type': str,
            'min_len': 0,
            'max_len': 100
        },
        'pet': {
            'type': dict,
            'schema': pet_schema,
        },
    })

    testdict = {
        'name': 'Lisa Simpson',
        'pet': {'animal': 'cat', 'name': 'Snowball', 'age': 6},
    }
    schema.validate(testdict)

    testdict = {
        'name': 'Bart Simpson',
        'pet': {'animal': 'dog', 'name': "Santa's Little Helper", 'ignored': 10},
    }
    schema.validate(testdict)

    with pytest.raises(TypeError):
        testdict = {
            'name': 'A',
            'pet': {'animal': 'B', 'name': 5},
        }
        schema.validate(testdict)

    with pytest.raises(ValueError):
        testdict = {
            'name': 'A',
            'pet': {'animal': 'B', 'name': 'C', 'age': -111},
        }
        schema.validate(testdict)
