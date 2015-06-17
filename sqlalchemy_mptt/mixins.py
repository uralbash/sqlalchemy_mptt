#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
SQLAlchemy nested sets mixin
"""
from sqlalchemy import Column, ForeignKey, Index, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.session import Session

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
            Index('%s_lft_idx' % cls.__tablename__, "lft"),
            Index('%s_rgt_idx' % cls.__tablename__, "rgt"),
            Index('%s_level_idx' % cls.__tablename__, "level"),
        )

    @classmethod
    def __declare_first__(cls):
        cls.__mapper__.batch = False

    @classmethod
    def get_pk_name(cls):
        return getattr(cls, 'sqlalchemy_mptt_pk_name', 'id')

    @classmethod
    def get_pk_column(cls):
        return getattr(cls, cls.get_pk_name())

    @classmethod
    def get_pk_with_class_name(cls):
        pk_name = cls.get_pk_name()
        return '%s.%s' % (cls.__name__, pk_name)

    @declared_attr
    def tree_id(cls):
        return Column("tree_id", Integer)

    @declared_attr
    def parent_id(cls):
        pk = cls.get_pk_column()
        if not pk.name:
            pk.name = cls.get_pk_name()

        return Column("parent_id", Integer,
                      ForeignKey('%s.%s' % (cls.__tablename__, pk.name),
                                 ondelete='CASCADE'))

    @declared_attr
    def parent(cls):
        pk = getattr(cls, cls.get_pk_name())
        return relationship(
            cls, primaryjoin=lambda: pk == cls.parent_id,
            order_by=lambda: cls.left,
            backref=backref('children', cascade="all,delete",
                            order_by=lambda: cls.left),
            remote_side=cls.get_pk_with_class_name(),
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

    def move_inside(self, parent_id):
        """ Moving one node of tree inside another

        For example see:

        * :mod:`sqlalchemy_mptt.tests.TestTree.test_move_inside_function`
        * :mod:`sqlalchemy_mptt.tests.TestTree.test_move_inside_to_the_same_parent_function`
        """  # noqa
        session = Session.object_session(self)
        self.parent_id = parent_id
        self.mptt_move_inside = parent_id
        session.add(self)

    def move_after(self, node_id):
        """ Moving one node of tree after another

        For example see :mod:`sqlalchemy_mptt.tests.TestTree.test_move_after_function`
        """  # noqa
        session = Session.object_session(self)
        self.parent_id = self.parent_id
        self.mptt_move_after = node_id
        session.add(self)

    def move_before(self, node_id):
        """ Moving one node of tree before another

        For example see:

        * :mod:`sqlalchemy_mptt.tests.TestTree.test_move_before_function`
        * :mod:`sqlalchemy_mptt.tests.TestTree.test_move_before_to_other_tree`
        * :mod:`sqlalchemy_mptt.tests.TestTree.test_move_before_to_top_level`
        """
        session = Session.object_session(self)
        table = _get_tree_table(self.__mapper__)
        pk = getattr(table.c, self.get_pk_column().name)
        node = session.query(table).filter(pk == node_id).one()
        self.parent_id = node.parent_id
        self.mptt_move_before = node_id
        session.add(self)

    def leftsibling_in_level(self):
        """ Node to the left of the current node at the same level

        For example see :mod:`sqlalchemy_mptt.tests.TestTree.test_leftsibling_in_level`
        """  # noqa
        table = _get_tree_table(self.__mapper__)
        session = Session.object_session(self)
        current_lvl_nodes = session.query(table)\
            .filter_by(level=self.level).filter_by(tree_id=self.tree_id)\
            .filter(table.c.lft < self.left).order_by(table.c.lft).all()
        if current_lvl_nodes:
            return current_lvl_nodes[-1]
        return None

    @classmethod
    def _node_of_get_tree_method(cls, node, json, json_fields):
        """ Helper method for ``get_tree`` and ``get_tree_reqursively``.
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
    def get_tree(cls, session, json=False, json_fields=None):
        """ This function generate tree of current node in dict or json format.

        Args:
            session (:mod:`sqlalchemy.orm.session.Session`): SQLAlchemy session

        Kwargs:
            json (bool): if True return JSON jqTree format
            json_fields (function): append custom fields in JSON

        Example:

        * :mod:`sqlalchemy_mptt.tests.TestTree.test_get_tree`
        * :mod:`sqlalchemy_mptt.tests.TestTree.test_get_json_tree`
        * :mod:`sqlalchemy_mptt.tests.TestTree.test_get_json_tree_with_custom_field`
        """  # noqa
        nodes = session.query(cls)\
            .order_by(cls.tree_id, cls.level, cls.left).all()
        tree = []
        nodes_of_level = {}

        def get_node_id(node):
            return getattr(node, node.get_pk_name())

        for node in nodes:
            result = cls._node_of_get_tree_method(node, json, json_fields)
            parent_id = node.parent_id
            if parent_id:  # for nodes with parent
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

    @classmethod
    def rebuild_tree(cls, session, tree_id):
        """ This function rebuid tree.

        Args:
            session (:mod:`sqlalchemy.orm.session.Session`): SQLAlchemy session
            tree_id (int or str): id of tree

        Example:

        * :mod:`sqlalchemy_mptt.tests.TestTree.test_rebuild`
        """
        session.query(cls).filter_by(tree_id=tree_id)\
            .update({cls.left: 0, cls.right: 0, cls.level: 0})
        top = session.query(cls).filter_by(parent_id=None)\
            .filter_by(tree_id=tree_id).one()
        top.left = left = 1
        top.right = right = 2
        top.level = level = 1

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
