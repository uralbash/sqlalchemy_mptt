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

from sqlalchemy import Column, event, ForeignKey, Index, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.session import Session

from .events import mptt_before_delete, mptt_before_insert, mptt_before_update


class BaseNestedSets(object):
    @declared_attr
    def __table_args__(cls):
        return (
            Index('%s_lft_idx' % cls.__tablename__, "lft"),
            Index('%s_rgt_idx' % cls.__tablename__, "rgt"),
            Index('%s_level_idx' % cls.__tablename__, "level"),
        )

    __mapper_args__ = {
        'batch': False  # allows extension to fire for each
                        # instance before going to the next.
    }

    @declared_attr
    def tree_id(cls):
        return Column("tree_id", Integer)

    @declared_attr
    def parent_id(cls):
        return Column("parent_id", Integer,
                      ForeignKey('%s.id' % cls.__tablename__,
                                 ondelete='CASCADE'))

    @declared_attr
    def parent(cls):
        return relationship(cls, primaryjoin=lambda: cls.id == cls.parent_id,
                            order_by=lambda: cls.left,
                            backref=backref('children', cascade="all,delete",
                                            order_by=lambda: cls.left),
                            remote_side=[cls.id],  # for show in sacrud relation
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

    @classmethod
    def register_tree(cls):
        event.listen(cls, "before_insert", mptt_before_insert)
        event.listen(cls, "before_update", mptt_before_update)
        event.listen(cls, "before_delete", mptt_before_delete)

    def move_inside(self, parent_id):
        session = Session.object_session(self)
        self.parent_id = parent_id
        session.add(self)

    def move_after(self, node_id):
        session = Session.object_session(self)
        self.parent_id = self.parent_id
        self.mptt_move_after = node_id
        session.add(self)

    @classmethod
    def get_tree(cls, session, json=False, json_fields=None):
        def recursive_node_to_dict(node):
            result = {'node': node}
            if json:
                # jqTree or jsTree format
                result = {'id': node.id, 'label': node.__repr__()}
                if json_fields:
                    result.update(json_fields(node))
            children = [recursive_node_to_dict(c) for c in node.children]
            if children:
                result['children'] = children
            return result

        nodes = session.query(cls).filter_by(parent_id=None)\
            .order_by(cls.tree_id).all()
        tree = []
        for node in nodes:
            tree.append(recursive_node_to_dict(node))

        return tree

    @classmethod
    def rebuild_tree(cls, session, tree_id):
        session.query(cls).filter_by(tree_id=tree_id)\
            .update({cls.left: 0, cls.right: 0, cls.level: 0})
        top = session.query(cls).filter_by(parent_id=None)\
            .filter_by(tree_id=tree_id).one()
        top.left = left = 1
        top.right = right = 2
        top.level = level = 1

        def reqursive(children, left, right, level):
            level = level + 1
            for i, node in enumerate(children):
                same_level_right = children[i-1].right
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
                reqursive(node.children, left, right, level)

        reqursive(top.children, left, right, level)

    @classmethod
    def rebuild(cls, session, tree_id=None):
        trees = session.query(cls).filter_by(parent_id=None)
        if tree_id:
            trees = trees.filter_by(tree_id=tree_id)
        for tree in trees:
            cls.rebuild_tree(session, tree.tree_id)
