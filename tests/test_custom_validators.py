#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from schemadict import schemadict, STANDARD_VALIDATORS


def test_example_modulo():
    """TODO"""

    def is_divisible(value, comp_value, key, _):
        if value % comp_value != 0:
            raise ValueError(f"{key!r} is not divisible by {comp_value}")

    my_validators = STANDARD_VALIDATORS
    my_validators[int]['%'] = is_divisible

    s = schemadict({'my_num': {'type': int, '%': 3}}, validators=my_validators)

    s.validate({'my_num': 33})
    with pytest.raises(ValueError):
        s.validate({'my_num': 4})


def test_example_my_class():
    """TODO"""

    class MyOcean:
        has_dolphins = True
        has_plastic = False

    def has_dolphins(value, comp_value, key, _):
        if getattr(value, 'has_dolphins') is not comp_value:
            raise ValueError(f"{key!r} does not have dolphins")

    my_validators = STANDARD_VALIDATORS
    my_validators.update({MyOcean: {'has_dolphins': has_dolphins}})

    schema_ocean = schemadict(
        {'ocean': {'type': MyOcean, 'has_dolphins': True}},
        validators=my_validators,
    )

    ocean1 = MyOcean()
    schema_ocean.validate({'ocean': ocean1})

    ocean2 = MyOcean()
    ocean2.has_dolphins = False
    with pytest.raises(ValueError):
        schema_ocean.validate({'ocean': ocean2})
