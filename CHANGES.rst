Versions releases 0.2.x & above
###############################

0.3.0 (Unreleased)
==================

see issues #63, #87, #89 & #90

- Support for joined-table inheritance
- Restrict to Python & PyPy 3.7 - 3.9
- Restrict to SQLA 1.0 - 1.3
- Fixes race condition with garbage collection on PyPy versions

0.2.5 (2019-07-23)
==================

see issue #64

- Added similar `django_mptt` methods `get_siblings` and `get_children`

0.2.4 (2018-12-14)
==================

see PR #61

- Allow to specify ordering of path_to_root

0.2.3 (2018-06-03)
==================

see issue #57

- Fix rebuild tree
- Added support node's identifier start from 0

0.2.2 (2017-10-05)
==================

see issue #56

- Added custom default root level. Support Django style level=0

0.2.1 (2016-01-23)
==================

see PR #51

- fix of index columns names

0.2.0 (2015-11-13)
==================

see PR #50

- Changed ``parent_id`` to dynamically match the type of the primary_key
- exposed drilldown_tree's logic and path_to_root's logic as both instance and
  class level method
