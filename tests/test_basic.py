#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

import pytest

from schemadict import schemadict, SchemaError


def time_now():
    return datetime.strftime(datetime.now(), '%H:%M')


SCHEMA_1 = schemadict({
    '__REQUIRED_KEYS': ['name', 'age'],
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
    '__REQUIRED_KEYS': ['name', 'age'],
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


SCHEMA_4 = schemadict({
    'time': {
        'type': str,
        'default': time_now
    },
    'person': {
        'type': str,
        'default': 'C.Lindbergh'
    },
    'age': {
        'type': int
    },
    'pets': {
        'type': dict,
        'schema': {
            'dog': {'type': bool, 'default': None},
            'cat': {'type': bool}
        },
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


def test_primitive_bool():
    """Check type 'bool'"""

    schema = schemadict({
        '__REQUIRED_KEYS': ['job_done'],
        'job_done': {'type': bool}
    })

    schema.validate({'job_done': True})
    schema.validate({'job_done': True, 'some_other_key': 'value_is_ignored'})

    with pytest.raises(TypeError):
        schema.validate({'job_done': 100})

    with pytest.raises(KeyError):
        schema.validate({'required_key_is_missing': True})

    # # TODO: Check if schema itself is correct
    # schema.update({'key_not_allowed_in_schema': 1})


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
            'item_schema': schema_city
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


def test_default_value_dict():
    """Test 'get_default_value_dict()'"""

    defaults = SCHEMA_1.get_default_value_dict()
    assert defaults == SCHEMA_1_DEFAULT_VALUE_DICT

    defaults = SCHEMA_4.get_default_value_dict()
    assert isinstance(defaults['time'], str)

    # Time may vary
    del SCHEMA_4_DEFAULT_VALUE_DICT['time']
    del defaults['time']

    assert defaults == SCHEMA_4_DEFAULT_VALUE_DICT


def test_version():
    from schemadict.__version__ import __version__
    print(__version__)
