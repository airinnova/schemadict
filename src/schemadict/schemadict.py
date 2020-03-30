#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Copyright 2019-2020 Airinnova AB and the Schemadict authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------

# Author: Aaron Dettmann

"""
Schema dictionaries
"""

from inspect import isclass
from numbers import Number


class Nothing:
    """Special 'type' used for checks"""
    pass


class SchemaError(Exception):
    """Raised if the schema dictionary is ill-defined"""
    pass


class Validators:
    """
    Collection of validators
    """

    @staticmethod
    def is_type(value, exp_type, err_msg=''):
        if isinstance(exp_type, dict):
            pass
            # TODO
        if not isinstance(value, exp_type):
            raise TypeError(err_msg)

    @staticmethod
    def is_gt(value, comp_value, err_msg=''):
        if not value > comp_value:
            raise ValueError(err_msg)

    @staticmethod
    def is_lt(value, comp_value, err_msg=''):
        if not value < comp_value:
            raise ValueError(err_msg)

    @staticmethod
    def is_le(value, comp_value, err_msg=''):
        if not value <= comp_value:
            raise ValueError(err_msg)

    @staticmethod
    def is_ge(value, comp_value, err_msg=''):
        if not value >= comp_value:
            raise ValueError(err_msg)

    @staticmethod
    def has_min_len(value, min_len, err_msg=''):
        if not len(value) >= min_len:
            raise ValueError(err_msg)

    @staticmethod
    def has_max_len(value, max_len, err_msg=''):
        if not len(value) <= max_len:
            raise ValueError(err_msg)

    @staticmethod
    def check_item_types(iterable, exp_item_type, err_msg=''):
        if not all(isinstance(item, exp_item_type) for item in iterable):
            raise TypeError(err_msg)


class ValidatorDict(dict):
    """
    Map 'type' (=key) and validator functions

    Raise 'SchemaError' if meta schema for 'type' is not defined
    """

    def __missing__(self, key):
        raise SchemaError(f"Meta schema not defined for {key!r}")


_VAL_TYPE = {'type': Validators.is_type}

_VAL_NUM_REL = {
    **_VAL_TYPE,
    '>': Validators.is_gt,
    '<': Validators.is_lt,
    '>=': Validators.is_ge,
    '<=': Validators.is_le,
}

_VAL_COUNTABLE = {
    **_VAL_TYPE,
    'min_len': Validators.has_min_len,
    'max_len': Validators.has_max_len,
}
_VAL_ITERABLE = {
    **_VAL_COUNTABLE,
    'item_types': Validators.check_item_types,
}

STANDARD_VALIDATORS = ValidatorDict({
    bool: _VAL_TYPE,
    int: _VAL_NUM_REL,
    float: _VAL_NUM_REL,
    str: _VAL_COUNTABLE,
    list: _VAL_ITERABLE,
    tuple: _VAL_ITERABLE,
})


class schemadict(dict):
    """
    A 'schemadict' is a dictionary that defines an expected format for how some
    other dictionary should be formatted. Schemadicts provide a 'validate()'
    method that checks if the test dictionary is conform with the schema.

    The schema validation is loosely inspired by JSON schema, see:

    * https://json-schema.org/understanding-json-schema/reference/index.html
    """

    SPECIAL_KEY_CHECK_REQ_KEYS = '__REQUIRED_KEYS'
    SPECIAL_KEY_LITERAL_EQUAL = '__EQUAL'

    SPECIAL_KEYS = [
        SPECIAL_KEY_CHECK_REQ_KEYS,
        SPECIAL_KEY_LITERAL_EQUAL,
    ]

    SPECIAL_VALUE_ANY_CLASS_TYPE = '__ANY_CLASS_TYPE'
    SPECIAL_VALUES = [
        SPECIAL_VALUE_ANY_CLASS_TYPE,
    ]

    # Define the allowed schema in terms of a schema dict
    # TODO: rethink --> validator objects instead !?
    # TODO: add type dict and 'schema' key
    # TODO: add 'default' key (can be None, same type as 'type', callable...)
    META_SCHEMA = {
        bool: {
            SPECIAL_KEY_CHECK_REQ_KEYS: ['type'],
            'type': {SPECIAL_KEY_LITERAL_EQUAL: bool},
        },
        int: {
            SPECIAL_KEY_CHECK_REQ_KEYS: ['type'],
            'type': {SPECIAL_KEY_LITERAL_EQUAL: int},
            '>': {'type': Number},
            '<': {'type': Number},
            '<=': {'type': Number},
            '>=': {'type': Number},
        },
        float: {
            SPECIAL_KEY_CHECK_REQ_KEYS: ['type'],
            'type': {SPECIAL_KEY_LITERAL_EQUAL: float},
            '>': {'type': Number},
            '<': {'type': Number},
            '<=': {'type': Number},
            '>=': {'type': Number},
        },
        str: {
            SPECIAL_KEY_CHECK_REQ_KEYS: ['type'],
            'type': {SPECIAL_KEY_LITERAL_EQUAL: str},
            'min_len': {'type': Number},
            'max_len': {'type': Number},
        },
        list: {
            SPECIAL_KEY_CHECK_REQ_KEYS: ['type'],
            'type': {SPECIAL_KEY_LITERAL_EQUAL: list},
            'min_len': {'type': Number},
            'max_len': {'type': Number},
            'item_types': {'type': SPECIAL_VALUE_ANY_CLASS_TYPE},
        },
        tuple: {
            SPECIAL_KEY_CHECK_REQ_KEYS: ['type'],
            'type': {SPECIAL_KEY_LITERAL_EQUAL: tuple},
            'min_len': {'type': Number},
            'max_len': {'type': Number},
            'item_types': {'type': SPECIAL_VALUE_ANY_CLASS_TYPE},
        },
    }

    VALIDATORS = STANDARD_VALIDATORS

    def _check_special_key(self, key, value, testdict):
        if key == self.SPECIAL_KEY_CHECK_REQ_KEYS:
            self.check_req_keys_in_dict(value, testdict)

        elif key == self.SPECIAL_KEY_LITERAL_EQUAL:
            if value != testdict[key]:
                # TODO: Add error message
                raise ValueError

    def _check_special_values(self, key, value, testdict):
        if value == self.SPECIAL_VALUE_ANY_CLASS_TYPE:
            if not isclass(testdict[key]):
                raise ValueError(f"Value for key {key!r} must be a class")

    @staticmethod
    def check_req_keys_in_dict(req_keys, testdict):
        """
        Check that required keys are in a test dictionary

        Args:
            :req_keys: List of keys required in the test dictionary
            :testdict: Test dictionary

        Raises:
            :KeyError: If a required key is not found in the test dictionary
        """

        # TODO: check that req_keys is list of strings !?

        testdict_keys = list(testdict.keys())
        for req_key in req_keys:
            if req_key not in testdict_keys:
                raise KeyError(f"Required key {req_key!r} not found in testdict")

    def validate(self, testdict):
        """
        Check that a dictionary conforms to a schema dictionary. This function
        will raise an error if the 'testdict' is not in agreement with the
        schema.

        Args:
            :testdict: (dict) dictionary to test against the schema

        Raises:
            :KeyError: if test dictionary does not have a required key
            :SchemaError: if the schema itself is ill-defined
            :TypeError: if test dictionary has a value of wrong type
            :ValueError: if test dictionary has a value of wrong 'size'
        """

        # TODO: validate that the schema itself is valid

        self._validate(testdict)

    def _validate(self, testdict):
        """Validate 'testdict' against 'self' (without schema validation)"""

        for schemadict_key, schemadict_value in self.items():
            # Treat special keys separately
            if schemadict_key in self.SPECIAL_KEYS:
                self._check_special_key(schemadict_key, schemadict_value, testdict)
                continue

            # Treat special values separately
            if schemadict_value in self.SPECIAL_VALUES:
                self._check_special_values(schemadict_key, schemadict_value, testdict)
                continue

            testdict_value = testdict.get(schemadict_key, None)

            # Continue if testdict does not have corresponding schemadict_value.
            # Note that required keys are checked separately.
            if testdict_value is None:
                continue

            # Basic type check (every schema entry must define a type)
            schemadict_type = schemadict_value.get('type', None)
            # ===== 'type' =====
            Validators.is_type(
                testdict_value,
                schemadict_type,
                f"Unexpected type for key {schemadict_key!r}. " +
                f"Expected {schemadict_type}, got {type(testdict_value)}."
            )

            # TYPE: dict
            if schemadict_type is dict:
                sub_schemadict = schemadict_value.get('schema', None)
                if sub_schemadict is not None:
                    schemadict(sub_schemadict).validate(testdict_value)
                    continue

            for validator_key, validator in self.VALIDATORS[schemadict_type].items():
                exp_value = schemadict_value.get(validator_key, None)
                if exp_value is not None:
                    validator(testdict_value, exp_value, err_msg='')

    def get_default_value_dict(self):
        """
        Return a dictionary with default values based on a schema dict

        Default values are genereated as follows:
            * If a key 'default' exists, the corresponding value will be used
                * If value is callable object, then the called value will be used
                * If value is non-callable, the value itself will be used
            * If no key, 'default' exists, 'type' will be called (if callable type)
            * Otherwise the default value will be None

        Example:

        .. code:: python
            from datetime import datetime

            def time_now():
                return datetime.strftime(datetime.now(), '%H:%S')

            schemadict = {
                'time': {
                    type': str,
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
            }

        The function will return

        .. code:: python
            defaults = {
                'time': '08:40',
                'person': 'C.Lindbergh',
                'age': 0,
                'pets': {
                    'dog': None,
                    'cat': False,
                }
            }
        """

        defaults = {}
        for key, value in self.items():
            if key in self.SPECIAL_KEYS:
                continue

            # ----- Basic type check -----
            schemadict_type = value.get('type', None)
            if schemadict_type is None:
                raise SchemaError(f"Expected type is not defined in schema (key: {key})")

            # ----- Recursion -----
            if schemadict_type is dict:
                defaults[key] = schemadict(value.get('schema', {})).get_default_value_dict()
                continue

            # ----- Set default value -----
            # Hint: default value could be intentionally set to None
            default_value = value.get('default', Nothing())
            if not isinstance(default_value, Nothing):
                if callable(default_value):
                    defaults[key] = default_value()
                else:
                    defaults[key] = default_value
                # TODO: maybe check that defaults[key] has type schemadict_type
            elif callable(schemadict_type):
                defaults[key] = schemadict_type()
            else:
                defaults[key] = None

        return defaults
