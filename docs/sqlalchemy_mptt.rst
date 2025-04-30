:mod:`sqlalchemy_mptt` package
==============================

Events
------

Base events
~~~~~~~~~~~

.. automodule:: sqlalchemy_mptt.events

    .. autofunction:: mptt_before_insert
    .. autofunction:: mptt_before_delete
    .. autofunction:: mptt_before_update
    .. autoclass:: TreesManager

Hidden method
~~~~~~~~~~~~~

    .. autofunction:: _insert_subtree

Mixins
------

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
-----

.. automodule:: sqlalchemy_mptt.tests.test_events
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: sqlalchemy_mptt.tests.test_inheritance
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: sqlalchemy_mptt.tests.test_mixins
    :members:
    :undoc-members:
    :show-inheritance:

Cases tests
~~~~~~~~~~~

.. automodule:: sqlalchemy_mptt.tests.cases.edit_node
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: sqlalchemy_mptt.tests.cases.get_node
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: sqlalchemy_mptt.tests.cases.get_tree
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: sqlalchemy_mptt.tests.cases.initialize
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: sqlalchemy_mptt.tests.cases.integrity
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: sqlalchemy_mptt.tests.cases.move_node
    :members:
    :undoc-members:
    :show-inheritance:
