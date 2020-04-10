.. image:: https://img.shields.io/pypi/v/schemadict.svg?style=flat
   :target: https://pypi.org/project/schemadict/
   :alt: Latest PyPI version

.. image:: https://readthedocs.org/projects/schemadict/badge/?version=latest
    :target: https://schemadict.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/license-Apache%202-blue.svg
    :target: https://github.com/airinnova/schemadict/blob/master/LICENSE.txt
    :alt: License

.. image:: https://travis-ci.org/airinnova/schemadict.svg?branch=master
    :target: https://travis-ci.org/airinnova/schemadict
    :alt: Build status

.. image:: https://codecov.io/gh/airinnova/schemadict/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/airinnova/schemadict
    :alt: Coverage

|

.. image:: https://raw.githubusercontent.com/airinnova/schemadict/master/docs/source/_static/images/logo.png
   :target: https://github.com/airinnova/schemadict/
   :alt: logo

A *schemadict* is a regular Python dictionary which specifies the type and format of values for some given key. To check if a test dictionary is conform with the expected schema, *schemadict* provides the `validate()` method. If the test dictionary is ill-defined, an error will be thrown, otherwise `None` is returned.

Examples
========

**Basic usage**

.. code:: python

    >>> from schemadict import schemadict

    >>> schema = schemadict({
    ...     'name': {
    ...         'type': str,
    ...         'min_len': 3,
    ...         'max_len': 12,
    ...     },
    ...     'age': {
    ...         'type': int,
    ...         '>=': 0,
    ...         '<': 150,
    ...     },
    ... })
    >>>
    >>> testdict = {'name': 'Neil', 'age': 55}
    >>> schema.validate(testdict)
    >>>

    >>> testdict = {'name': 'Neil', 'age': -12}
    >>> schema.validate(testdict)
    Traceback (most recent call last):
        ...
    ValueError: 'age' too small: expected >= 0, but was -12
    >>>

    >>> testdict = {'name': 'Neil', 'age': '55'}
    >>> schema.validate(testdict)
    Traceback (most recent call last):
        ...
    TypeError: unexpected type for 'age': expected <class 'int'>, but was <class 'str'>
    >>>

**Nested schemadict**

.. code:: python

    >>> schema_city = schemadict({
    ...     'name': {
    ...         'type': str
    ...     },
    ...     'population': {
    ...         'type': int,
    ...         '>=': 0,
    ...     },
    ... })
    >>>
    >>> schema_country = schemadict({
    ...     'name': {'type': str},
    ...     'cities': {
    ...         'type': list,
    ...         'item_type': dict,
    ...         'item_schema': schema_city,
    ...     },
    ... })
    >>>
    >>> test_country = {
    ...     'name': 'Neverland',
    ...     'cities': [
    ...         {'name': 'Faketown', 'population': 3},
    ...         {'name': 'Evergreen', 'population': True},
    ...     ],
    ... }
    >>>
    >>> schema_country.validate(test_country)
    Traceback (most recent call last):
        ...
    TypeError: unexpected type for 'population': expected <class 'int'>, but was <class 'bool'>
    >>>

**Custom validation functions**

Each *type* (``int``, ``bool``, ``str``, etc.) defines its own set of validation keywords and corresponding test functions. The dictionary ``STANDARD_VALIDATORS`` provided by the ``schemadict`` module contains the default validation functions for the Python's built-in types. However, it is also possible to modify or extend this dictionary with custom validation functions.

.. code:: python

    >>> from schemadict import schemadict, STANDARD_VALIDATORS

    >>> # Add a custom validation function
    >>> def is_divisible(value, comp_value, key):
    ...     if value % comp_value != 0:
    ...             raise ValueError(f"{key!r} is not divisible by {comp_value}")
    ...
    ...
    ...
    >>>

    >>> # Update the standard validator dictionary
    >>> my_validators = STANDARD_VALIDATORS
    >>> my_validators[int]['%'] = is_divisible

    >>> # Register the updated validator dictionary in the new schemadict instance
    >>> s = schemadict({'my_num': {'type': int, '%': 3}}, validators=my_validators)

    >>> s.validate({'my_num': 33})
    >>> s.validate({'my_num': 4})
    Traceback (most recent call last):
        ...
    ValueError: 'my_num' is not divisible by 3
    >>>

It is also possible to define *custom types* and *custom test functions* as shown in the following example.

.. code:: python

    >>> from schemadict import schemadict, STANDARD_VALIDATORS

    >>> class MyOcean:
    ...     has_dolphins = True
    ...     has_plastic = False
    ...
    >>>

    >>> def has_dolphins(value, comp_value, key):
    ...     if getattr(value, 'has_dolphins') is not comp_value:
    ...         raise ValueError(f"{key!r} does not have dolphins")
    ...
    >>>

    >>> my_validators = STANDARD_VALIDATORS
    >>> my_validators.update({MyOcean: {'has_dolphins': has_dolphins}})
    >>>

    >>> schema_ocean = schemadict(
    ...     {'ocean': {'type': MyOcean, 'has_dolphins': True}},
    ...     validators=my_validators,
    ... )
    >>>

    >>> ocean1 = MyOcean()
    >>> schema_ocean.validate({'ocean': ocean1})
    >>>

    >>> ocean2 = MyOcean()
    >>> ocean2.has_dolphins = False
    >>> schema_ocean.validate({'ocean': ocean2})
    Traceback (most recent call last):
        ...
    ValueError: 'ocean' does not have dolphins


Full documentation: https://schemadict.readthedocs.io/

Features
========

What *schemadict* offers:

* Built-in support for Python's primitive types
* Specify *required* and *optional* keys
* Validate *nested* schemas
* Add custom validation functions to built-in types
* Add custom validation functions to custom types

Features currently in development

* Regex support for strings
* Metaschema validation
* Lazy validation and summary of all errors
* Allow schema variations: schmea 1 OR schema 2
* Add support for validation of type `number.Number`

Installation
============

*Schemadict* is available on `PyPI <https://pypi.org/project/schemadict/>`_ and may simply be installed with

.. code::

    pip install schemadict

Idea
====

*Schemadict* is loosely inspired by `JSON schema <https://json-schema.org/>`_ and `jsonschema <https://github.com/Julian/jsonschema>`_, a JSON schema validator for Python.

License
=======

**License:** Apache-2.0
