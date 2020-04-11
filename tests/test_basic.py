#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections.abc import MutableMapping
from datetime import datetime

import pytest

from schemadict import schemadict, SchemaError


def time_now():
    return datetime.strftime(datetime.now(), '%H:%M')


SCHEMA_1 = schemadict({
    '$required_keys': ['name', 'age'],
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
    'is_working': {
        'type': bool
    }
})

SCHEMA_1_DEFAULT_VALUE_DICT = schemadict({
    'name': '',
    'age': 0,
    'is_working': False,
})

# Simple nested schema
SCHEMA_2 = schemadict({
    '$required_keys': ['name', 'age'],
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
    'child': {
        'type': dict,
        'schema': SCHEMA_1,
    }
})

SCHEMA_3 = schemadict({
    'fruits': {
        'type': list,
        'min_len': 3,
        'max_len': 3,
        'item_types': str,
    },
    'numbers': {
        'type': tuple,
        'min_len': 3,
        'item_types': (int, float),
    },
})


SCHEMA_4_DEFAULT_VALUE_DICT = {
    'time': '08:40',
    'person': 'C.Lindbergh',
    'age': 0,
    'pets': {
        'dog': None,
        'cat': False,
    }
}


def test_schemadict_type():
    """Test type of schemadict"""

    assert isinstance(schemadict(), MutableMapping)
    assert isinstance(schemadict(), schemadict)


def test_basic():
    """Check basic functionality of 'schemadict'"""

    test = {
        'name': 'Neil',
        'age': 22,
        'is_working': True,
    }
    SCHEMA_1.validate(test)
    schemadict(schemadict(schemadict(SCHEMA_1))).validate(test)  # Must be equivalent to above call

    test = {
        'name': 'Neil',
        'age': 200,  # Value too large
    }
    with pytest.raises(ValueError):
        SCHEMA_1.validate(test)
        schemadict(schemadict(schemadict(SCHEMA_1))).validate(test)  # Must be equivalent to above call

    test = {
        'name': 'Neil',
        'age': -1,  # Value too small
    }
    with pytest.raises(ValueError):
        SCHEMA_1.validate(test)

    test = {
        'name': 'Neil',
        # Required key 'age' is missing
    }
    with pytest.raises(KeyError):
        SCHEMA_1.validate(test)

    test = {
        'name': 'Neil NameTooLong',
        'age': 22,
    }
    with pytest.raises(ValueError):
        SCHEMA_1.validate(test)

    test = {
        'name': 'A',  # Name too short
        'age': 22,
    }
    with pytest.raises(ValueError):
        SCHEMA_1.validate(test)


def test_schema_error():
    """Test if type of schema is not defined"""

    schema = schemadict({'a': {'type': bool}})
    schema.validate({'a': True})

    # Schema not defined for custiom 'type'
    class MyOwnType:
        pass

    schema = schemadict({'a': {'type': MyOwnType}})

    with pytest.raises(SchemaError):
        schema.validate({'a': MyOwnType()})


def test_nested_dict():
    """Test nested schemadicts"""

    test = {
        'name': 'Neil',
        'age': 22,
        'child': {
            'name': 'Test',
            'age': 3,
        }
    }
    SCHEMA_1.validate(test)  # Validation against schema 1 must still work
    SCHEMA_2.validate(test)

    test = {
        'name': 'Neil',
        'age': 22,
        'child': {
            'name': 'Test',
            'age': -3,  # Wrong age
        }
    }
    with pytest.raises(ValueError):
        SCHEMA_2.validate(test)


def test_arrays():
    """Test schema with array"""

    test = {
        'fruits': ['apple', 'pear', 'strawberry'],
        'numbers': (3.14159, 42, 1792, 5050),
    }
    SCHEMA_3.validate(test)

    test = {
        'fruits': ['apple', 'pear', 'strawberry'],
        'numbers': (3.14159, 42, 1792, 5050, 'string_not_allowed'),
    }
    with pytest.raises(TypeError):
        SCHEMA_3.validate(test)


def test_list_with_subschemas():

    schema_city = schemadict({
        'name': {
            'type': str
        },
        'population': {
            'type': int,
            '>=': 0
        },
    })

    schema_country = schemadict({
        'name': {'type': str},
        'cities': {
            'type': list,
            'item_type': dict,
            'item_schemadict': schema_city
        },
    })

    test_country = {
        'name': 'Neverland',
        'cities': [
            {'name': 'Faketown', 'population': 3},
            {'name': 'Evergreen', 'population': True},  # bool not allowed here
        ]
    }

    with pytest.raises(TypeError):
        schema_country.validate(test_country)

    # Fix the incorrect type
    test_country['cities'][1]['population'] = 1
    schema_country.validate(test_country)


def test_testdict_type():
    """Raise TypeError if input of validate() is not a dict"""

    schema = schemadict({'a': {'type': bool}})

    schema.validate({'a': True})

    with pytest.raises(TypeError):
        schema.validate(True)

    with pytest.raises(TypeError):
        schema.validate(144)

    with pytest.raises(TypeError):
        schema.validate('a: True')


def test_version():
    from schemadict.__version__ import __version__
    print(__version__)
