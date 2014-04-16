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

from sqlalchemy import (and_, case, Column, event, ForeignKey, Index, Integer,
                        select)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref, relationship


class NestedSetsExtension(object):

    @staticmethod
    def before_insert(mapper, connection, instance):
        if not instance.parent_id:
            instance.left = 1
            instance.right = 2
            instance.level = 1
            instance.tree_id = instance.id
        else:
            table = mapper.mapped_table
            right_most_sibling, parent_tree_id, parent_level = connection.execute(
                select([table.c.rgt, table.c.tree_id, table.c.level]).
                where(table.c.id == instance.parent_id)
            ).fetchone()

            instance.tree_id = parent_tree_id

            # update key of current tree
            connection.execute(
                table.update(
                    and_(table.c.rgt >= right_most_sibling,
                         table.c.tree_id == parent_tree_id)
                ).values(
                    lft=case(
                        [(table.c.lft > right_most_sibling,
                          table.c.lft + 2)],
                        else_=table.c.lft
                    ),
                    rgt=case(
                        [(table.c.rgt >= right_most_sibling,
                          table.c.rgt + 2)],
                        else_=table.c.rgt
                    )
                )
            )

            instance.level = parent_level + 1
            instance.left = right_most_sibling
            instance.right = right_most_sibling + 1

    @staticmethod
    def after_delete(mapper, connection, instance):

        table = mapper.mapped_table
        lft = instance.left
        rgt = instance.right
        tree_id = instance.tree_id
        delta = rgt - lft + 1

        # Delete node or baranch of node
        # DELETE FROM tree WHERE lft >= $lft AND rgt <= $rgt
        connection.execute(
            table.delete(and_(table.c.lft >= lft, table.c.rgt <= rgt,
                              table.c.tree_id == tree_id))
        )

        if instance.parent_id:
            """ Update key of current tree

                UPDATE tree
                SET left_id = CASE
                        WHEN left_id > $leftId THEN left_id - $delta
                        ELSE left_id
                    END,
                    right_id = CASE
                        WHEN right_id >= $rightId THEN right_id - $delta
                        ELSE right_id
                    END
            """
            connection.execute(
                table.update(
                    and_(table.c.rgt >= rgt, table.c.tree_id == tree_id))
                .values(
                    lft=case(
                        [(table.c.lft > lft, table.c.lft - delta)],
                        else_=table.c.lft
                    ),
                    rgt=case(
                        [(table.c.rgt >= rgt, table.c.rgt - delta)],
                        else_=table.c.rgt
                    )
                )
            )


class BaseNestedSets(NestedSetsExtension):
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
        return Column(Integer, ForeignKey('%s.id' % cls.__tablename__))

    @declared_attr
    def tree(cls):
        return relationship(cls, primaryjoin=lambda: cls.id == cls.tree_id,
                            backref=backref('children_tree'),  # for delete
                            remote_side=[cls.id],  # for show in sacrud
                            post_update=True   # solve CircularDependencyError
                            )

    @declared_attr
    def parent_id(cls):
        return Column(Integer, ForeignKey('%s.id' % cls.__tablename__))

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
        return Column(Integer, nullable=False, default=0)

    @classmethod
    def register_tree(cls):
        event.listen(cls, "before_insert", cls.before_insert)
        event.listen(cls, "after_delete", cls.after_delete)
