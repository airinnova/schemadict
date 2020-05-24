Welcome to |name|'s documentation!
==================================

.. image:: _static/images/logo.svg
    :alt: Logo
    :width: 120 px

.. code::

    >>> from schemadict import schemadict

    >>> schema = schemadict({'myNumber': {'type': int, '>': 0}})
    >>> schema.validate({'myNumber': 4})
    >>> schema.validate({'myNumber': -20})
    Traceback (most recent call last):
        ...
    ValueError: 'myNumber' too small: expected > 0, but was -20

.. toctree::
   :maxdepth: 2
   :caption: User guide

   user_guide/installation
   user_guide/usage

.. toctree::
   :maxdepth: 1
   :caption: API documentation

   dev_doc/modules

.. toctree::
   :maxdepth: 1
   :caption: Changelog

   CHANGELOG

:Authors:
    |author1|

:Licence:
    |license|
