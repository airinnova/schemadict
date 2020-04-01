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

from collections import OrderedDict
from inspect import isclass
from numbers import Number


class SchemaError(Exception):
    """Raised if the schema dictionary is ill-defined"""
    pass


class Validators:
    """
    Collection of validator functions

    All validator functions must accept three arguments in the order listed
    below. The actual variable names may differ depending on context.

    Args:
        :value: value to be checked
        :exp_value: expected value or comparison object
        :key: dictionary key (used in error message)
    """

    @classmethod
    def is_type(cls, value, exp_type, key):
        # TODO????
        # if isinstance(exp_type, dict):
        #     cls.check_schemadict(value, exp_type, key)

        # Note: isinstance(True, int) evaluates to True
        if type(value) not in (exp_type,):
            raise TypeError(
                f"unexpected type for {key!r}: " +
                f"expected {exp_type!r}, but was {type(value)}"
            )

    @staticmethod
    def is_gt(value, comp_value, key):
        if not value > comp_value:
            raise ValueError(
                f"{key!r} too small: " +
                f"expected > {comp_value!r}, but was {value!r}"
            )

    @staticmethod
    def is_lt(value, comp_value, key):
        if not value < comp_value:
            raise ValueError(
                f"{key!r} too large: " +
                f"expected < {comp_value!r}, but was {value!r}"
            )

    @classmethod
    def is_ge(cls, value, comp_value, key):
        if not value >= comp_value:
            raise ValueError(
                f"{key!r} too small: " +
                f"expected >= {comp_value!r}, but was {value!r}"
            )

    @staticmethod
    def is_le(value, comp_value, key):
        if not value <= comp_value:
            raise ValueError(
                f"{key!r} too large: " +
                f"expected <= {comp_value!r}, but was {value!r}"
            )

    @staticmethod
    def has_min_len(value, min_len, key):
        if not len(value) >= min_len:
            raise ValueError(
                f"length of {key!r} too small: " +
                f"expected >= {min_len!r}, but was {len(value)!r}"
            )

    @staticmethod
    def has_max_len(value, max_len, key):
        if not len(value) <= max_len:
            raise ValueError(
                f"length of {key!r} too large: " +
                f"expected <= {max_len!r}, but was {len(value)!r}"
            )

    @staticmethod
    def check_item_types(iterable, exp_item_type, key):
        if not all(isinstance(item, exp_item_type) for item in iterable):
            raise TypeError(
                f"unexpected type for item in iterable {key!r}: " +
                f"expected {exp_item_type!r}"
            )

    @classmethod
    def check_item_schema(cls, iterable, item_schema, key):
        for item in iterable:
            cls.check_schemadict(item, item_schema, key)

    @staticmethod
    def check_schemadict(testdict, schema, key):
        schemadict(schema).validate(testdict)


class ValidatorDict(OrderedDict):
    """
    Use to map 'type' (=key) and validator functions

    Raise 'SchemaError' if meta schema for 'type' is not defined.
    """
    def __missing__(self, key):
        raise SchemaError(f"meta-schema not defined for {key!r}")


# Check type (required by all validators)
_VAL_TYPE = {'type': Validators.is_type}

# Check numerical relations (int, float, Number)
_VAL_NUM_REL = {
    **_VAL_TYPE,
    '>': Validators.is_gt,
    '<': Validators.is_lt,
    '>=': Validators.is_ge,
    '<=': Validators.is_le,
}

# Check countable objects (list, tuple, str)
_VAL_COUNTABLE = {
    **_VAL_TYPE,
    'min_len': Validators.has_min_len,
    'max_len': Validators.has_max_len,
}

# Check iterable objects (list, tuple)
_VAL_ITERABLE = {
    **_VAL_COUNTABLE,
    'item_types': Validators.check_item_types,
    'item_schema': Validators.check_item_schema,
}

_VAL_SUBSCHEMA = {
    **_VAL_TYPE,
    'schema': Validators.check_schemadict,
}

# Validators for primitive types
STANDARD_VALIDATORS = ValidatorDict({
    bool: _VAL_TYPE,
    int: _VAL_NUM_REL,
    float: _VAL_NUM_REL,
    str: _VAL_COUNTABLE,
    list: _VAL_ITERABLE,
    tuple: _VAL_ITERABLE,
    dict: _VAL_SUBSCHEMA,
    # schemadict: _VAL_SUBSCHEMA,
})


class schemadict(dict):
    """
    A *schemadict* is a regular Python dictionary which specifies the type and
    format of values for some given key. To check if a test dictionary is
    conform with the expected schema, *schemadict* provides the `validate()`
    method. If the test dictionary is ill-defined, an error will be thrown,
    otherwise `None` is returned.
    """

    # Special 'type' used for checks
    class Nothing:
        pass

    # ===== TODO (START) =====
    # TODO: find better solution!?
    SPECIAL_KEY_CHECK_REQ_KEYS = '__REQUIRED_KEYS'
    # SPECIAL_KEY_LITERAL_EQUAL = '__EQUAL'

    SPECIAL_KEYS = [
        SPECIAL_KEY_CHECK_REQ_KEYS,
        # SPECIAL_KEY_LITERAL_EQUAL,
    ]

    SPECIAL_VALUE_ANY_CLASS_TYPE = '__ANY_CLASS_TYPE'
    SPECIAL_VALUES = [
        SPECIAL_VALUE_ANY_CLASS_TYPE,
    ]
    # ===== TODO (END) =====

    # ===== TODO (START) =====
    # TODO: add type dict and 'schema' key
    # TODO: write more succinct
    # TODO: add 'default' key (can be None, same type as 'type', callable...)

    # Define the allowed schema in terms of a schema dict
    # META_SCHEMA = {
    #     bool: {
    #         SPECIAL_KEY_CHECK_REQ_KEYS: ['type'],
    #         'type': {SPECIAL_KEY_LITERAL_EQUAL: bool},
    #     },
    #     int: {
    #         SPECIAL_KEY_CHECK_REQ_KEYS: ['type'],
    #         'type': {SPECIAL_KEY_LITERAL_EQUAL: int},
    #         '>': {'type': Number},
    #         '<': {'type': Number},
    #         '<=': {'type': Number},
    #         '>=': {'type': Number},
    #     },
    #     float: {
    #         SPECIAL_KEY_CHECK_REQ_KEYS: ['type'],
    #         'type': {SPECIAL_KEY_LITERAL_EQUAL: float},
    #         '>': {'type': Number},
    #         '<': {'type': Number},
    #         '<=': {'type': Number},
    #         '>=': {'type': Number},
    #     },
    #     str: {
    #         SPECIAL_KEY_CHECK_REQ_KEYS: ['type'],
    #         'type': {SPECIAL_KEY_LITERAL_EQUAL: str},
    #         'min_len': {'type': Number},
    #         'max_len': {'type': Number},
    #     },
    #     list: {
    #         SPECIAL_KEY_CHECK_REQ_KEYS: ['type'],
    #         'type': {SPECIAL_KEY_LITERAL_EQUAL: list},
    #         'min_len': {'type': Number},
    #         'max_len': {'type': Number},
    #         'item_types': {'type': SPECIAL_VALUE_ANY_CLASS_TYPE},
    #     },
    #     tuple: {
    #         SPECIAL_KEY_CHECK_REQ_KEYS: ['type'],
    #         'type': {SPECIAL_KEY_LITERAL_EQUAL: tuple},
    #         'min_len': {'type': Number},
    #         'max_len': {'type': Number},
    #         'item_types': {'type': SPECIAL_VALUE_ANY_CLASS_TYPE},
    #     },
    # }
    # ===== TODO (END) =====

    VALIDATORS = STANDARD_VALIDATORS

    def _check_special_key(self, key, value, testdict):
        if key == self.SPECIAL_KEY_CHECK_REQ_KEYS:
            self.check_req_keys_in_dict(value, testdict)

        elif key == self.SPECIAL_KEY_LITERAL_EQUAL:
            if value != testdict[key]:
                # ===== TODO =====
                # TODO: Add error message
                raise ValueError

    # def _check_special_values(self, key, value, testdict):
    #     if value == self.SPECIAL_VALUE_ANY_CLASS_TYPE:
    #         if not isclass(testdict[key]):
    #             raise ValueError(f"Value for key {key!r} must be a class")

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

        # ===== TODO =====
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

        for sd_key, sd_value in self.items():
            # ===== TODO (START) =====
            # TODO: find better solution
            # Treat special keys/values separately
            if sd_key in self.SPECIAL_KEYS:
                self._check_special_key(sd_key, sd_value, testdict)
                continue
###            if sd_value in self.SPECIAL_VALUES:
###                self._check_special_values(sd_key, sd_value, testdict)
###                continue
            # ===== TODO (END) =====

            td_value = testdict.get(sd_key, None)
            # Continue if testdict does not have corresponding sd_value.
            # Note that required keys are checked separately.
            if td_value is None:
                continue

            for validator_key, validator in self.VALIDATORS[sd_value['type']].items():
                exp_value = sd_value.get(validator_key, None)
                if exp_value is not None:
                    validator(td_value, exp_value, sd_key)

    # ===== TODO =====
    # TODO: continue here --------------------------------------------------
    def get_default_value_dict(self):
        """
        Return a dictionary with default values based on a schema dict

        Default values are generated as follows:
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
            default_value = value.get('default', self.Nothing())
            if not isinstance(default_value, self.Nothing):
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
