#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
# Copyright © 2016 Jiri Kuncar <jiri.kuncar@gmail.com>
#
# Distributed under terms of the MIT license.

"""
SQLAlchemy nested sets mixin
"""
# SQLAlchemy
from sqlalchemy import Index, Column, Integer, ForeignKey, asc, desc
from sqlalchemy.orm import backref, relationship, object_session
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative import declared_attr

# local
from .events import _get_tree_table


class BaseNestedSets(object):
    """ Base mixin for MPTT model.

    Example:

    .. code::

        from sqlalchemy import Boolean, Column, create_engine, Integer
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker

        from sqlalchemy_mptt.mixins import BaseNestedSets

        Base = declarative_base()


        class Tree(Base, BaseNestedSets):
            __tablename__ = "tree"

            id = Column(Integer, primary_key=True)
            visible = Column(Boolean)

            def __repr__(self):
                return "<Node (%s)>" % self.id
    """

    @declared_attr
    def __table_args__(cls):
        return (
            Index('%s_lft_idx' % cls.__tablename__, cls.left.name),
            Index('%s_rgt_idx' % cls.__tablename__, cls.right.name),
            Index('%s_level_idx' % cls.__tablename__, cls.level.name),
        )

    @classmethod
    def __declare_first__(cls):
        cls.__mapper__.batch = False

    @classmethod
    def get_pk_name(cls):
        return getattr(cls, 'sqlalchemy_mptt_pk_name', 'id')

    @classmethod
    def get_default_level(cls):
        '''
        Compatibility with Django MPTT: level value for root node.
        See https://github.com/uralbash/sqlalchemy_mptt/issues/56
        '''
        return getattr(cls, 'sqlalchemy_mptt_default_level', 1)

    @classmethod
    def get_pk_column(cls):
        return getattr(cls, cls.get_pk_name())

    @declared_attr
    def tree_id(cls):
        return Column("tree_id", Integer)

    @declared_attr
    def parent_id(cls):
        pk = cls.get_pk_column()
        if not pk.name:
            pk.name = cls.get_pk_name()

        return Column(
            "parent_id",
            pk.type,
            ForeignKey(
                '{}.{}'.format(cls.__tablename__, pk.name),
                ondelete='CASCADE'
            )
        )

    @declared_attr
    def parent(self):
        return relationship(
            self,
            order_by=lambda: self.left,
            foreign_keys=[self.parent_id],
            remote_side='{}.{}'.format(self.__name__, self.get_pk_name()),
            backref=backref(
                'children',
                cascade="all,delete",
                order_by=lambda: (self.tree_id, self.left)
            )
        )

    @declared_attr
    def left(cls):
        return Column("lft", Integer, nullable=False)

    @declared_attr
    def right(cls):
        return Column("rgt", Integer, nullable=False)

    @declared_attr
    def level(cls):
        return Column("level", Integer, nullable=False, default=0)

    @hybrid_method
    def is_ancestor_of(self, other, inclusive=False):
        """ class or instance level method which returns True if self is
        ancestor (closer to root) of other else False. Optional flag
        `inclusive` on whether or not to treat self as ancestor of self.

        For example see:

        * :mod:`sqlalchemy_mptt.tests.cases.integrity.test_hierarchy_structure`
        """
        if inclusive:
            return (self.tree_id == other.tree_id) \
                & (self.left <= other.left) \
                & (other.right <= self.right)
        return (self.tree_id == other.tree_id) \
            & (self.left < other.left) \
            & (other.right < self.right)

    @hybrid_method
    def is_descendant_of(self, other, inclusive=False):
        """ class or instance level method which returns True if self is
        descendant (farther from root) of other else False.  Optional flag
        `inclusive` on whether or not to treat self as descendant of self.

        For example see:

        * :mod:`sqlalchemy_mptt.tests.cases.integrity.test_hierarchy_structure`
        """
        return other.is_ancestor_of(self, inclusive)

    def move_inside(self, parent_id):
        """ Moving one node of tree inside another

        For example see:

        * :mod:`sqlalchemy_mptt.tests.cases.move_node.test_move_inside_function`
        * :mod:`sqlalchemy_mptt.tests.cases.move_node.test_move_inside_to_the_same_parent_function`
        """  # noqa
        session = Session.object_session(self)
        self.parent_id = parent_id
        self.mptt_move_inside = parent_id
        session.add(self)

    def move_after(self, node_id):
        """ Moving one node of tree after another

        For example see :mod:`sqlalchemy_mptt.tests.cases.move_node.test_move_after_function`
        """  # noqa
        session = Session.object_session(self)
        self.parent_id = self.parent_id
        self.mptt_move_after = node_id
        session.add(self)

    def move_before(self, node_id):
        """ Moving one node of tree before another

        For example see:

        * :mod:`sqlalchemy_mptt.tests.cases.move_node.test_move_before_function`
        * :mod:`sqlalchemy_mptt.tests.cases.move_node.test_move_before_to_other_tree`
        * :mod:`sqlalchemy_mptt.tests.cases.move_node.test_move_before_to_top_level`
        """  # noqa
        session = Session.object_session(self)
        table = _get_tree_table(self.__mapper__)
        pk = getattr(table.c, self.get_pk_column().name)
        node = session.query(table).filter(pk == node_id).one()
        self.parent_id = node.parent_id
        self.mptt_move_before = node_id
        session.add(self)

    def leftsibling_in_level(self):
        """ Node to the left of the current node at the same level

        For example see
        :mod:`sqlalchemy_mptt.tests.cases.get_tree.test_leftsibling_in_level`
        """  # noqa
        table = _get_tree_table(self.__mapper__)
        session = Session.object_session(self)
        current_lvl_nodes = session.query(table) \
            .filter_by(level=self.level).filter_by(tree_id=self.tree_id) \
            .filter(table.c.lft < self.left).order_by(table.c.lft).all()
        if current_lvl_nodes:
            return current_lvl_nodes[-1]
        return None

    @classmethod
    def _node_to_dict(cls, node, json, json_fields):
        """ Helper method for ``get_tree``.
        """
        if json:
            pk_name = node.get_pk_name()
            # jqTree or jsTree format
            result = {'id': getattr(node, pk_name), 'label': node.__repr__()}
            if json_fields:
                result.update(json_fields(node))
        else:
            result = {'node': node}
        return result

    @classmethod
    def _base_query(cls, session=None):
        return session.query(cls)

    def _base_query_obj(self, session=None):
        if not session:
            session = object_session(self)
        return self._base_query(session)

    @classmethod
    def _base_order(cls, query, order=asc):
        return query.order_by(order(cls.tree_id))\
            .order_by(order(cls.level))\
            .order_by(order(cls.left))

    @classmethod
    def get_tree(cls, session=None, json=False, json_fields=None, query=None):
        """ This method generate tree of current node table in dict or json
        format. You can make custom query with attribute ``query``. By default
        it return all nodes in table.

        Args:
            session (:mod:`sqlalchemy.orm.session.Session`): SQLAlchemy session

        Kwargs:
            json (bool): if True return JSON jqTree format
            json_fields (function): append custom fields in JSON
            query (function): it takes :class:`sqlalchemy.orm.query.Query`
            object as an argument, and returns in a modified form

                ::

                    def query(nodes):
                        return nodes.filter(node.__class__.tree_id.is_(node.tree_id))

                    node.get_tree(session=DBSession, json=True, query=query)

        Example:

        * :mod:`sqlalchemy_mptt.tests.cases.get_tree.test_get_tree`
        * :mod:`sqlalchemy_mptt.tests.cases.get_tree.test_get_json_tree`
        * :mod:`sqlalchemy_mptt.tests.cases.get_tree.test_get_json_tree_with_custom_field`
        """  # noqa
        tree = []
        nodes_of_level = {}

        # handle custom query
        nodes = cls._base_query(session)
        if query:
            nodes = query(nodes)
        nodes = cls._base_order(nodes).all()

        # search minimal level of nodes.
        min_level = min([node.level for node in nodes] or [None])

        def get_node_id(node):
            return getattr(node, node.get_pk_name())

        for node in nodes:
            result = cls._node_to_dict(node, json, json_fields)
            parent_id = node.parent_id
            if node.level != min_level:  # for cildren
                # Find parent in the tree
                if parent_id not in nodes_of_level.keys():
                    continue
                if 'children' not in nodes_of_level[parent_id]:
                    nodes_of_level[parent_id]['children'] = []
                # Append node to parent
                nl = nodes_of_level[parent_id]['children']
                nl.append(result)
                nodes_of_level[get_node_id(node)] = nl[-1]
            else:  # for top level nodes
                tree.append(result)
                nodes_of_level[get_node_id(node)] = tree[-1]
        return tree

    def _drilldown_query(self, nodes=None):
        table = self.__class__
        if not nodes:
            nodes = self._base_query_obj()
        return nodes.filter(self.is_ancestor_of(table, inclusive=True))

    def drilldown_tree(self, session=None, json=False, json_fields=None):
        """ This method generate a branch from a tree, begining with current
        node.

        For example:

            node7.drilldown_tree()

            .. code::

                level           Nested sets example
                1                    1(1)22       ---------------------
                        _______________|_________|_________            |
                       |               |         |         |           |
                2    2(2)5           6(4)11      |      12(7)21        |
                       |               ^         |         ^           |
                3    3(3)4       7(5)8   9(6)10  | 13(8)16   17(10)20  |
                                                 |    |          |     |
                4                                | 14(9)15   18(11)19  |
                                                 |                     |
                                                  ---------------------

        Example in tests:

            * :mod:`sqlalchemy_mptt.tests.cases.get_tree.test_drilldown_tree`
        """
        if not session:
            session = object_session(self)
        return self.get_tree(
            session,
            json=json,
            json_fields=json_fields,
            query=self._drilldown_query
        )

    def path_to_root(self, session=None):
        """Generate path from a leaf or intermediate node to the root.

        For example:

            node11.path_to_root()

            .. code::

                level           Nested sets example

                                 -----------------------------------------
                1               |    1(1)22                               |
                        ________|______|_____________________             |
                       |        |      |                     |            |
                       |         ------+---------            |            |
                2    2(2)5           6(4)11      | --     12(7)21         |
                       |               ^             |   /      \         |
                3    3(3)4       7(5)8   9(6)10      ---/----    \        |
                                                    13(8)16 |  17(10)20   |
                                                       |    |     |       |
                4                                   14(9)15 | 18(11)19    |
                                                            |             |
                                                             -------------
        """
        table = self.__class__
        query = self._base_query_obj(session=session)
        query = query.filter(table.is_ancestor_of(self, inclusive=True))
        return self._base_order(query, order=desc)

    @classmethod
    def rebuild_tree(cls, session, tree_id):
        """ This method rebuid tree.

        Args:
            session (:mod:`sqlalchemy.orm.session.Session`): SQLAlchemy session
            tree_id (int or str): id of tree

        Example:

        * :mod:`sqlalchemy_mptt.tests.cases.get_tree.test_rebuild`
        """
        session.query(cls).filter_by(tree_id=tree_id)\
            .update({cls.left: 0, cls.right: 0, cls.level: 0})
        top = session.query(cls).filter_by(parent_id=None)\
            .filter_by(tree_id=tree_id).one()
        top.left = left = 1
        top.right = right = 2
        top.level = level = cls.get_default_level()

        def recursive(children, left, right, level):
            level = level + 1
            for i, node in enumerate(children):
                same_level_right = children[i - 1].right
                left = left + 1

                if i > 0:
                    left = left + 1
                if same_level_right:
                    left = same_level_right + 1

                right = left + 1
                node.left = left
                node.right = right
                parent = node.parent

                j = 0
                while parent:
                    parent.right = right + 1 + j
                    parent = parent.parent
                    j += 1

                node.level = level
                recursive(node.children, left, right, level)

        recursive(top.children, left, right, level)

    @classmethod
    def rebuild(cls, session, tree_id=None):
        """ This function rebuid tree.

        Args:
            session (:mod:`sqlalchemy.orm.session.Session`): SQLAlchemy session

        Kwargs:
            tree_id (int or str): id of tree, default None

        Example:

        * :mod:`sqlalchemy_mptt.tests.TestTree.test_rebuild`
        """

        trees = session.query(cls).filter_by(parent_id=None)
        if tree_id:
            trees = trees.filter_by(tree_id=tree_id)
        for tree in trees:
            cls.rebuild_tree(session, tree.tree_id)
