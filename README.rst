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
        ...
    ValueError: 'age' too small: expected >= 0, but was -12
    >>>

    >>> testdict = {'name': 'Neil', 'age': '55'}
    >>> schema.validate(testdict)
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
    ...         '>=': 0
    ...     },
    ... })
    >>>
    >>> schema_country = schemadict({
    ...     'name': {'type': str},
    ...     'cities': {
    ...         'type': list,
    ...         'item_type': dict,
    ...         'item_schema': schema_city
    ...     },
    ... })
    >>>
    >>> test_country = {
    ...     'name': 'Neverland',
    ...     'cities': [
    ...         {'name': 'Faketown', 'population': 3},
    ...         {'name': 'Evergreen', 'population': True},
    ...     ]
    ... }
    >>>
    >>> schema_country.validate(test_country)
        ...
    TypeError: unexpected type for 'population': expected <class 'int'>, but was <class 'bool'>
    >>>

**Custom validation functions**

**TODO**

Full documentation: https://schemadict.readthedocs.io/

Features
========

Schemadicts supports

* Built-in support for Python's primitive types
* Specification of *required* and *optional* keys
* Validation of *nested* schemas
* Adding custom validator functions

Features currently in progress

* Metaschema validation
* Validation of subschemas in list or tuples
* Regex support for strings
* Lazy validation and summary of all errors

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
