0.1.9 (2015-09-24)
==================

- add option ``remove`` to ``sqlalchemy.events.TreesManager.register_mapper``

0.1.8 (2015-09-14)
==================

- add method ``_base_query_obj``

0.1.7 (2015-08-18)
==================

- add method ``path_to_root`` (see #46)
- add data integrity tests

0.1.6 (2015-07-03)
==================

- fix bug with ``get_tree`` when no rows in database.

0.1.5 (2015-06-25)
==================

- Add drilldown_tree method (see #41)
- Add custom ``query`` atribute to ``get_tree`` method

0.1.4 (2015-06-19)
==================

- delete method ``get_pk_with_class_name``

Bug Fixes
---------

- fix ``_get_tree_table`` function for inheritance models
