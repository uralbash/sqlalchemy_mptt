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

0.0.9 (2014-10-09)
==================

- Add MANIFEST.in
- New docs
- fixes in setup.py

0.0.8 (2014-08-15)
==================

- Add CONTRIBUTORS.txt

Features
--------

- Automatically register tree classes enhancement (#28)
- Added support polymorphic tree models (#24)

Bug Fixes
---------

- Fix expire left/right attributes of parent somewhen after the `before_insert` event (#30)
- Fix tree_id is incorrectly set to an existing tree if no parent is set (#23)
- Fix package is not installable if sqlalchemy is not (yet) installed (#22)

0.0.7 (2014-08-04)
==================

- Add LICENSE.txt

Bug Fixes
---------

- fix get_db_pk function


0.0.6 (2014-07-31)
==================

Bug Fixes
---------

-  Allow the primary key to not be named "id" #20. See https://github.com/ITCase/sqlalchemy_mptt/issues/20
