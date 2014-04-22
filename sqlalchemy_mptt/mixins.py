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

from events import mptt_after_delete, mptt_before_insert, mptt_before_update


class BaseNestedSets(object):
    __table_args__ = (
        Index('mptt_pages2_lft', "lft"),
        Index('mptt_pages2_rgt', "rgt"),
        Index('mptt_pages2_level', "level"),
    )
    __mapper_args__ = {
        'batch': False  # allows extension to fire for each
                        # instance before going to the next.
    }

    @declared_attr
    def tree_id(cls):
        return Column("tree_id", Integer,
                      ForeignKey('%s.id' % cls.__tablename__))

    @declared_attr
    def tree(cls):
        return relationship(cls, primaryjoin=lambda: cls.id == cls.tree_id,
                            backref=backref('children_tree'),  # for delete
                            remote_side=[cls.id],  # for show in sacrud
                            post_update=True   # solve CircularDependencyError
                            )

    @declared_attr
    def parent_id(cls):
        return Column("parent_id", Integer,
                      ForeignKey('%s.id' % cls.__tablename__))

    @declared_attr
    def parent(cls):
        return relationship(cls, primaryjoin=lambda: cls.id == cls.parent_id,
                            backref=backref('children'),  # for delete
                            remote_side=[cls.id]  # for show in sacrud relation
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
        event.listen(cls, "after_delete", mptt_after_delete)
        event.listen(cls, "before_update", mptt_before_update)
