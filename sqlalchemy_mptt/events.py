#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
SQLAlchemy events extension
"""
# standard library
import weakref

# SQLAlchemy
from sqlalchemy import and_, case, event, select, inspection
from sqlalchemy.orm import object_session
from sqlalchemy.sql import func
from sqlalchemy.orm.base import NO_VALUE


def _insert_subtree(
        table,
        connection,
        node_size,
        node_pos_left,
        node_pos_right,
        parent_pos_left,
        parent_pos_right,
        subtree,
        parent_tree_id,
        parent_level,
        node_level,
        left_sibling,
        table_pk
):
    # step 1: rebuild inserted subtree
    delta_lft = left_sibling['lft'] + 1
    if not left_sibling['is_parent']:
        delta_lft = left_sibling['rgt'] + 1
    delta_rgt = delta_lft + node_size - 1

    connection.execute(
        table.update(
            table_pk.in_(subtree)
        ).values(
            lft=table.c.lft - node_pos_left + delta_lft,
            rgt=table.c.rgt - node_pos_right + delta_rgt,
            level=table.c.level - node_level + parent_level + 1,
            tree_id=parent_tree_id
        )
    )

    # step 2: update key of right side
    connection.execute(
        table.update(
            and_(
                table.c.rgt > delta_lft - 1,
                table_pk.notin_(subtree),
                table.c.tree_id == parent_tree_id
            )
        ).values(
            rgt=table.c.rgt + node_size,
            lft=case(
                [
                    (
                        table.c.lft > left_sibling['lft'],
                        table.c.lft + node_size
                    )
                ],
                else_=table.c.lft
            )
        )
    )


def _get_tree_table(mapper):
    for table in mapper.tables:
        if all(key in table.c for key in ['level', 'lft', 'rgt', 'parent_id']):
            return table


def mptt_before_insert(mapper, connection, instance):
    """ Based on example
    https://bitbucket.org/zzzeek/sqlalchemy/src/73095b353124/examples/nested_sets/nested_sets.py?at=master
    """
    table = _get_tree_table(mapper)
    db_pk = instance.get_pk_column()
    table_pk = getattr(table.c, db_pk.name)

    if instance.parent_id is None:
        instance.left = 1
        instance.right = 2
        instance.level = instance.get_default_level()
        tree_id = connection.scalar(
            select(
                [
                    func.max(table.c.tree_id) + 1
                ]
            )
        ) or 1
        instance.tree_id = tree_id
    else:
        (parent_pos_left,
         parent_pos_right,
         parent_tree_id,
         parent_level) = connection.execute(
            select(
                [
                    table.c.lft,
                    table.c.rgt,
                    table.c.tree_id,
                    table.c.level
                ]
            ).where(
                table_pk == instance.parent_id
            )
        ).fetchone()

        # Update key of right side
        connection.execute(
            table.update(
                and_(table.c.rgt >= parent_pos_right,
                     table.c.tree_id == parent_tree_id)
            ).values(
                lft=case(
                    [
                        (
                            table.c.lft > parent_pos_right,
                            table.c.lft + 2
                        )
                    ],
                    else_=table.c.lft
                ),
                rgt=case(
                    [
                        (
                            table.c.rgt >= parent_pos_right,
                            table.c.rgt + 2
                        )
                    ],
                    else_=table.c.rgt
                )
            )
        )

        instance.level = parent_level + 1
        instance.tree_id = parent_tree_id
        instance.left = parent_pos_right
        instance.right = parent_pos_right + 1


def mptt_before_delete(mapper, connection, instance, delete=True):
    table = _get_tree_table(mapper)
    tree_id = instance.tree_id
    pk = getattr(instance, instance.get_pk_name())
    db_pk = instance.get_pk_column()
    table_pk = getattr(table.c, db_pk.name)
    lft, rgt = connection.execute(
        select(
            [
                table.c.lft,
                table.c.rgt
            ]
        ).where(
            table_pk == pk
        )
    ).fetchone()
    delta = rgt - lft + 1

    if delete:
        mapper.base_mapper.confirm_deleted_rows = False
        connection.execute(
            table.delete(
                table_pk == pk
            )
        )

    if instance.parent_id is not None or not delete:
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
                and_(
                    table.c.rgt > rgt,
                    table.c.tree_id == tree_id
                )
            ).values(
                lft=case(
                    [
                        (
                            table.c.lft > lft,
                            table.c.lft - delta
                        )
                    ],
                    else_=table.c.lft
                ),
                rgt=case(
                    [
                        (
                            table.c.rgt >= rgt,
                            table.c.rgt - delta
                        )
                    ],
                    else_=table.c.rgt
                )
            )
        )


def mptt_before_update(mapper, connection, instance):
    """ Based on this example:
        http://stackoverflow.com/questions/889527/move-node-in-nested-set
    """
    node_id = getattr(instance, instance.get_pk_name())
    table = _get_tree_table(mapper)
    db_pk = instance.get_pk_column()
    default_level = instance.get_default_level()
    table_pk = getattr(table.c, db_pk.name)
    mptt_move_inside = None
    left_sibling = None
    left_sibling_tree_id = None

    if hasattr(instance, 'mptt_move_inside'):
        mptt_move_inside = instance.mptt_move_inside

    if hasattr(instance, 'mptt_move_before'):
        (
            right_sibling_left,
            right_sibling_right,
            right_sibling_parent,
            right_sibling_level,
            right_sibling_tree_id
        ) = connection.execute(
            select(
                [
                    table.c.lft,
                    table.c.rgt,
                    table.c.parent_id,
                    table.c.level,
                    table.c.tree_id
                ]
            ).where(
                table_pk == instance.mptt_move_before
            )
        ).fetchone()
        current_lvl_nodes = connection.execute(
            select(
                [
                    table.c.lft,
                    table.c.rgt,
                    table.c.parent_id,
                    table.c.tree_id
                ]
            ).where(
                and_(
                    table.c.level == right_sibling_level,
                    table.c.tree_id == right_sibling_tree_id,
                    table.c.lft < right_sibling_left
                )
            )
        ).fetchall()
        if current_lvl_nodes:
            (
                left_sibling_left,
                left_sibling_right,
                left_sibling_parent,
                left_sibling_tree_id
            ) = current_lvl_nodes[-1]
            instance.parent_id = left_sibling_parent
            left_sibling = {
                'lft': left_sibling_left,
                'rgt': left_sibling_right,
                'is_parent': False
            }
        # if move_before to top level
        elif not right_sibling_parent:
            left_sibling_tree_id = right_sibling_tree_id - 1

    # if placed after a particular node
    if hasattr(instance, 'mptt_move_after'):
        (
            left_sibling_left,
            left_sibling_right,
            left_sibling_parent,
            left_sibling_tree_id
        ) = connection.execute(
            select(
                [
                    table.c.lft,
                    table.c.rgt,
                    table.c.parent_id,
                    table.c.tree_id
                ]
            ).where(
                table_pk == instance.mptt_move_after
            )
        ).fetchone()
        instance.parent_id = left_sibling_parent
        left_sibling = {
            'lft': left_sibling_left,
            'rgt': left_sibling_right,
            'is_parent': False
        }

    """ Get subtree from node

        SELECT id, name, level FROM my_tree
        WHERE left_key >= $left_key AND right_key <= $right_key
        ORDER BY left_key
    """
    subtree = connection.execute(
        select([table_pk])
        .where(
            and_(
                table.c.lft >= instance.left,
                table.c.rgt <= instance.right,
                table.c.tree_id == instance.tree_id
            )
        ).order_by(
            table.c.lft
        )
    ).fetchall()
    subtree = [x[0] for x in subtree]

    """ step 0: Initialize parameters.

        Put there left and right position of moving node
    """
    (
        node_pos_left,
        node_pos_right,
        node_tree_id,
        node_parent_id,
        node_level
    ) = connection.execute(
        select(
            [
                table.c.lft,
                table.c.rgt,
                table.c.tree_id,
                table.c.parent_id,
                table.c.level
            ]
        ).where(
            table_pk == node_id
        )
    ).fetchone()

    # if instance just update w/o move
    # XXX why this str() around parent_id comparison?
    if not left_sibling \
            and str(node_parent_id) == str(instance.parent_id) \
            and not mptt_move_inside:
        if left_sibling_tree_id is None:
            return

    # fix tree shorting
    if instance.parent_id is not None:
        (
            parent_id,
            parent_pos_right,
            parent_pos_left,
            parent_tree_id,
            parent_level
        ) = connection.execute(
            select(
                [
                    table_pk,
                    table.c.rgt,
                    table.c.lft,
                    table.c.tree_id,
                    table.c.level
                ]
            ).where(
                table_pk == instance.parent_id
            )
        ).fetchone()
        if node_parent_id is None and node_tree_id == parent_tree_id:
            instance.parent_id = None
            return

    # delete from old tree
    mptt_before_delete(mapper, connection, instance, False)

    if instance.parent_id is not None:
        """ Put there right position of new parent node (there moving node
            should be moved)
        """
        (
            parent_id,
            parent_pos_right,
            parent_pos_left,
            parent_tree_id,
            parent_level
        ) = connection.execute(
            select(
                [
                    table_pk,
                    table.c.rgt,
                    table.c.lft,
                    table.c.tree_id,
                    table.c.level
                ]
            ).where(
                table_pk == instance.parent_id
            )
        ).fetchone()
        # 'size' of moving node (including all it's sub nodes)
        node_size = node_pos_right - node_pos_left + 1

        # left sibling node
        if not left_sibling:
            left_sibling = {
                'lft': parent_pos_left,
                'rgt': parent_pos_right,
                'is_parent': True
            }

        # insert subtree in exist tree
        instance.tree_id = parent_tree_id
        _insert_subtree(
            table,
            connection,
            node_size,
            node_pos_left,
            node_pos_right,
            parent_pos_left,
            parent_pos_right,
            subtree,
            parent_tree_id,
            parent_level,
            node_level,
            left_sibling,
            table_pk
        )
    else:
        # if insert after
        if left_sibling_tree_id or left_sibling_tree_id == 0:
            tree_id = left_sibling_tree_id + 1
            connection.execute(
                table.update(
                    table.c.tree_id > left_sibling_tree_id
                ).values(
                    tree_id=table.c.tree_id + 1
                )
            )
        # if just insert
        else:
            tree_id = connection.scalar(
                select(
                    [
                        func.max(table.c.tree_id) + 1
                    ]
                )
            )

        connection.execute(
            table.update(
                table_pk.in_(
                    subtree
                )
            ).values(
                lft=table.c.lft - node_pos_left + 1,
                rgt=table.c.rgt - node_pos_left + 1,
                level=table.c.level - node_level + default_level,
                tree_id=tree_id
            )
        )


class _WeakDictBasedSet(weakref.WeakKeyDictionary, object):
    """
    In absence of a default weakset implementation, provide our own dict
    based solution.
    """

    def add(self, obj):
        self[obj] = None

    def discard(self, obj):
        super(_WeakDictBasedSet, self).pop(obj, None)

    def pop(self):
        return self.popitem()[0]


class _WeakDefaultDict(weakref.WeakKeyDictionary, object):

    def __getitem__(self, key):
        try:
            return super(_WeakDefaultDict, self).__getitem__(key)
        except KeyError:
            self[key] = value = _WeakDictBasedSet()
            return value


class TreesManager(object):
    """
    Manages events dispatching for all subclasses of a given class.
    """
    def __init__(self, base_class):
        self.base_class = base_class
        self.classes = set()
        self.instances = _WeakDefaultDict()

    def register_events(self, remove=False):
        for e, h in (
            ('before_insert', self.before_insert),
            ('before_update', self.before_update),
            ('before_delete', self.before_delete),
        ):
            is_event_exist = event.contains(self.base_class, e, h)
            if remove and is_event_exist:
                event.remove(self.base_class, e, h)
            elif not is_event_exist:
                event.listen(self.base_class, e, h, propagate=True)
        return self

    def register_factory(self, sessionmaker):
        """
        Registers this TreesManager instance to respond on
        `after_flush_postexec` events on the given session or session factory.
        This method returns the original argument, so that it can be used by
        wrapping an already existing instance:

        .. code-block:: python
            :linenos:

            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker, mapper
            from sqlalchemy_mptt.mixins import BaseNestedSets

            engine = create_engine('...')

            trees_manager = TreesManager(BaseNestedSets)
            trees_manager.register_mapper(mapper)

            Session = tree_manager.register_factory(
                sessionmaker(bind=engine)
            )

        A reference to this method, bound to a default instance of this class
        and already registered to a mapper, is importable directly from
        `sqlalchemy_mptt`:

        .. code-block:: python
            :linenos:

            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            from sqlalchemy_mptt import mptt_sessionmaker

            engine = create_engine('...')
            Session = mptt_sessionmaker(sessionmaker(bind=engine))
        """
        event.listen(sessionmaker, 'after_flush_postexec',
                     self.after_flush_postexec)
        return sessionmaker

    def before_insert(self, mapper, connection, instance):
        session = object_session(instance)
        self.instances[session].add(instance)
        mptt_before_insert(mapper, connection, instance)

    def before_update(self, mapper, connection, instance):
        session = object_session(instance)
        self.instances[session].add(instance)
        mptt_before_update(mapper, connection, instance)

    def before_delete(self, mapper, connection, instance):
        session = object_session(instance)
        self.instances[session].discard(instance)
        mptt_before_delete(mapper, connection, instance)

    def after_flush_postexec(self, session, context):
        """
        Event listener to recursively expire `left` and `right` attributes the
        parents of all modified instances part of this flush.
        """
        instances = self.instances[session]
        while instances:
            try:
                instance = instances.pop()
            except KeyError:
                break
            if instance not in session:
                continue
            parent = self.get_parent_value(instance)

            while parent != NO_VALUE and parent is not None:
                instances.discard(parent)
                session.expire(parent, ['left', 'right', 'tree_id', 'level'])
                parent = self.get_parent_value(parent)
            else:
                session.expire(instance, ['left', 'right', 'tree_id', 'level'])
                self.expire_session_for_children(session, instance)

    @staticmethod
    def get_parent_value(instance):
        return inspection.inspect(instance).attrs.parent.loaded_value

    @staticmethod
    def expire_session_for_children(session, instance):
        children = instance.children

        def expire_recursively(node):
            children = node.children
            for item in children:
                session.expire(item, ['left', 'right', 'tree_id', 'level'])
                expire_recursively(item)

        if children != NO_VALUE and children is not None:
            for item in children:
                session.expire(item, ['left', 'right', 'tree_id', 'level'])
                expire_recursively(item)
