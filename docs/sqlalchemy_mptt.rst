:mod:`sqlalchemy_mptt` package
=======================

Events
-----------------------------

Base events
~~~~~~~~~~~

.. automodule:: sqlalchemy_mptt.events

    .. autofunction:: mptt_before_insert
    .. autofunction:: mptt_before_delete
    .. autofunction:: mptt_before_update

Hidden method
~~~~~~~~~~~~~

    .. autofunction:: _insert_subtree

Mixins
-----------------------------

.. automodule:: sqlalchemy_mptt.mixins

    .. autoclass:: BaseNestedSets
        :members:

        .. automethod:: tree_id
        .. attribute:: parent_id
        .. attribute:: parent
        .. automethod:: left
        .. automethod:: right
        .. automethod:: level

Tests
----------------------------

.. automodule:: sqlalchemy_mptt.tests
    :members:
    :undoc-members:
    :show-inheritance:
