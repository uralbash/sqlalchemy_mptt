0.1.7 (2015-08-??)
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

0.1.3 (2015-06-17)
==================

- Add test for swap trees
- rename ``get_pk`` method to ``get_pk_name``
- rename ``get_db_pk`` method to ``get_pk_column``
- rename ``get_class_pk`` method to ``get_pk_with_class_name``

Bug Fixes
---------

- Fix order of elements in tree

0.1.2 (2015-04-22)
==================

Bug Fixes
---------

- Fix MANIFEST.in file

Deprecation
-----------

- Delete ``BaseNestedSets.register_tree`` method
- Delete ``BaseNestedSets.get_tree_recursively`` method

0.1.1 (2015-04-21)
==================

Features
--------

- Add test for rst docs and migrate on new itcase_sphinx_theme (#40)

Bug Fixes
---------

- Remove recursion from BaseNestedSets.get_tree method (#39)

0.1.0 (2014-11-18)
==================

Bug Fixes
---------

- Fix concurrency issue with multiple session (#36)
- Flushing the session now expire the instance and it's children (#33)
