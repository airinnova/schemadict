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

# Read:
# * https://treyhunner.com/2019/04/why-you-shouldnt-inherit-from-list-and-dict-in-python/
# * https://docs.python.org/3/library/abc.html
# * https://docs.python.org/3/library/collections.abc.html

from collections import OrderedDict
from collections.abc import MutableMapping
import re


class SchemaError(Exception):
    """Raised if the schema dictionary is ill-defined"""
    pass


class Validators:
    """
    Collection of validator functions

    All validator functions must accept four arguments in the order listed
    below. The actual variable names may differ depending on context.

    Args:
        :key: related dictionary key (used in error message)
        :test_value: value to be checked
        :exp_value: expected value or comparison object
        :sd_instance: instance of the schemadict from which tests are called

    Note:
        * In most cases the last argument (the schemadict instance) is not
          needed, and the test function may ignore the argument. However, in
          case the schemadict is instantiated with custom validator functions,
          these must be propagated when recursively checking nested data
          structures
    """

    @staticmethod
    def is_type(key, value, exp_type, _):
        # Note: isinstance(True, int) evaluates to True
        if type(value) not in (exp_type,):
            raise TypeError(
                f"unexpected type for {key!r}: " +
                f"expected {exp_type!r}, but was {type(value)}"
            )

    @staticmethod
    def is_gt(key, value, comp_value, _):
        if not value > comp_value:
            raise ValueError(
                f"{key!r} too small: " +
                f"expected > {comp_value!r}, but was {value!r}"
            )

    @staticmethod
    def is_lt(key, value, comp_value, _):
        if not value < comp_value:
            raise ValueError(
                f"{key!r} too large: " +
                f"expected < {comp_value!r}, but was {value!r}"
            )

    @staticmethod
    def is_ge(key, value, comp_value, _):
        if not value >= comp_value:
            raise ValueError(
                f"{key!r} too small: " +
                f"expected >= {comp_value!r}, but was {value!r}"
            )

    @staticmethod
    def is_le(key, value, comp_value, _):
        if not value <= comp_value:
            raise ValueError(
                f"{key!r} too large: " +
                f"expected <= {comp_value!r}, but was {value!r}"
            )

    @staticmethod
    def has_min_len(key, value, min_len, _):
        if not len(value) >= min_len:
            raise ValueError(
                f"length of {key!r} too small: " +
                f"expected >= {min_len!r}, but was {len(value)!r}"
            )

    @staticmethod
    def has_max_len(key, value, max_len, _):
        if not len(value) <= max_len:
            raise ValueError(
                f"length of {key!r} too large: " +
                f"expected <= {max_len!r}, but was {len(value)!r}"
            )

    @staticmethod
    def check_regex_match(key, string, pattern, _):
        if not re.match(pattern, string):
            raise ValueError(
                f"regex mismatch for {key!r}: " +
                f"expected pattern {pattern!r}, got {string!r}"
            )

    @staticmethod
    def check_item_types(key, iterable, exp_item_type, _):
        if not all(isinstance(item, exp_item_type) for item in iterable):
            raise TypeError(
                f"unexpected type for item in iterable {key!r}: " +
                f"expected {exp_item_type!r}"
            )

    @staticmethod
    def check_item_schema(key, iterable, item_schema, sd_instance):
        # TODO: check that iterables are not of type dict !?
        for item in iterable:
            sd_instance._check_test_obj_against_test_funcs(key, item_schema, item)

    @classmethod
    def check_item_schemadict(cls, key, iterable, item_schema, sd_instance):
        # TODO: check that iterables are of type dict !?
        for item in iterable:
            cls.check_schemadict(key, item, item_schema, sd_instance)

    @staticmethod
    def check_schemadict(key, testdict, schema, sd_instance):
        schemadict(schema, validators=sd_instance.validators).validate(testdict)


class ValidatorDict(OrderedDict):
    """
    Use to map 'type' (=key) and validator functions

    Raise 'SchemaError' if meta schema for 'type' is not defined.
    """
    def __missing__(self, key):
        raise SchemaError(f"validator functions not defined for {key!r}")


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

# Check string objects
_VAL_STRING = {
    **_VAL_COUNTABLE,
    'regex': Validators.check_regex_match,
}

# Check iterable objects (list, tuple)
_VAL_ITERABLE = {
    **_VAL_COUNTABLE,
    'item_types': Validators.check_item_types,
    # TODO: find better names !!!!
    'item_schema': Validators.check_item_schema,  # if each item is primitive type, but not a dictionary
    'item_schemadict': Validators.check_item_schemadict,  # if each item is a complex dictionary
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
    str: _VAL_STRING,
    list: _VAL_ITERABLE,
    tuple: _VAL_ITERABLE,
    dict: _VAL_SUBSCHEMA,
})


METAKEY_CHECK_REQ_KEYS = '$required_keys'


class schemadict(MutableMapping):
    """
    A *schemadict* is a dictionary that specifies the type and format of values
    for some given key. To check if a test dictionary is conform with the
    expected schema, *schemadict* provides the `validate()` method. If the test
    dictionary is ill-defined, an error will be thrown, otherwise `None` is
    returned.
    """

    def __init__(self, *args, validators=STANDARD_VALIDATORS, **kwargs):
        self.mapping = {}
        self.update(*args, **kwargs)

        # Default validator functions (map validator functions to keywords for each type)
        self.validators = validators
        self.metakeys = [METAKEY_CHECK_REQ_KEYS]

    def __setitem__(self, key, value):
        # Only allow string as keys
        if not isinstance(key, str):
            raise SchemaError(f"invalid key {key!r}: must be of type {str}, not {type(key)}")
        # ============================================================
        # TODO: Perform meta schema validation here...
        # ============================================================
        self.mapping[key] = value

    def __getitem__(self, key):
        return self.mapping[key]

    def __delitem__(self, key):
        del self.mapping[key]

    def __iter__(self):
        return iter(self.mapping)

    def __len__(self):
        return len(self.mapping)

    def __str__(self):
        return str(self.mapping)

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.mapping!r})"

    def _check_special_key(self, key, value, testdict):
        if key == METAKEY_CHECK_REQ_KEYS:
            self.check_req_keys_in_dict(value, testdict)

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
                raise KeyError(f"required key {req_key!r} not found")

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

        # Check that testdict actually is a dictionary
        Validators.is_type('$testdict', testdict, dict, self)

        for sd_key, sd_value in self.items():

            # Treat special keys/values separately
            # TODO: find better solution
            if sd_key in self.metakeys:
                self._check_special_key(sd_key, sd_value, testdict)
                continue

            td_value = testdict.get(sd_key, None)
            # Continue if testdict does not have corresponding sd_value.
            # Note that required keys are checked separately.
            if td_value is None:
                continue

            self._check_test_obj_against_test_funcs(sd_key, sd_value, td_value)

    def _check_test_obj_against_test_funcs(self, sd_key, sd_value, td_value):
        """
        For a given key, validate the test dictionary value against each test
        function defined by the schemadict entry

        Args:
            :sd_key: common key for test dictionary and schemadict entry
            :sd_value: mapping of test keywords and validator functions
            :td_value: test dictionary value (object to test)
        """

        for validator_key, validator_func in self.validators[sd_value['type']].items():
            exp_value = sd_value.get(validator_key, None)
            if exp_value is not None:
                validator_func(sd_key, td_value, exp_value, self)
