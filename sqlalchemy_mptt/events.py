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
from sqlalchemy import and_, case, select


def _insert_subtree(table, connection, node_size,
                    node_pos_left, node_pos_right,
                    parent_pos_left, parent_pos_right, subtree,
                    parent_tree_id, parent_level, node_level):
    """ step 1: rebuild inserted subtree
    """
    left_node = (None, parent_pos_left, parent_pos_right)

    delta = -1
    delta_lft = left_node[1] + 2 + delta
    delta_rgt = left_node[1] + node_size

    connection.execute(
        table.update(table.c.id.in_(subtree))
        .values(
            lft=table.c.lft-node_pos_left+delta_lft,
            rgt=table.c.rgt-node_pos_right+delta_rgt,
            level=table.c.level-node_level+parent_level+1,
            tree_id=parent_tree_id
        )
    )

    """ step 2: update key of right side
    """
    connection.execute(
        table.update(
            and_(table.c.rgt > parent_pos_left,
                 table.c.id.notin_(subtree),
                 table.c.tree_id == parent_tree_id)
        ).values(
            rgt=table.c.rgt + node_size,
            lft=case(
                [(table.c.lft > parent_pos_left,
                  table.c.lft + node_size)],
                else_=table.c.lft
            )
        )
    )


def mptt_before_insert(mapper, connection, instance):
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


def mptt_before_delete(mapper, connection, instance, delete=True):
    table = mapper.mapped_table
    tree_id = instance.tree_id
    lft, rgt = connection.execute(
        select([table.c.lft, table.c.rgt]).where(table.c.id == instance.id)
    ).fetchone()
    delta = rgt - lft + 1

    if delete:
        mapper.confirm_deleted_rows = False
        connection.execute(
            table.delete(table.c.id == instance.id)
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
                and_(table.c.rgt > rgt, table.c.tree_id == tree_id))
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


def mptt_before_update(mapper, connection, instance):
    """ Based on this example:
        http://stackoverflow.com/questions/889527/move-node-in-nested-set
    """
    table = mapper.mapped_table
    """ step 0: Initialize parameters.
    """
    # put there id of moving node
    node_id = instance.id

    # put there left and right position of moving node
    (node_pos_left, node_pos_right,
        node_tree_id, node_parent_id, node_level) = connection.execute(
        select([table.c.lft, table.c.rgt,
                table.c.tree_id, table.c.parent_id, table.c.level])
        .where(table.c.id == node_id)
    ).fetchone()

    """ Get subtree from node

        SELECT id, name, level FROM my_tree
        WHERE left_key >= $left_key AND right_key <= $right_key
        ORDER BY left_key
    """
    subtree = connection.execute(
        select([table.c.id])
        .where(and_(table.c.lft >= node_pos_left,
                    table.c.rgt <= node_pos_right,
                    table.c.tree_id == node_tree_id))
        .order_by(table.c.lft)
    ).fetchall()
    subtree = map(lambda x: x[0], subtree)

    """ delete from old tree
    """
    mptt_before_delete(mapper, connection, instance, False)

    """ step 0: Reinitialize parameters.
    """
    # put there id of moving node
    node_id = instance.id

    # put there left and right position of moving node
    (node_pos_left, node_pos_right,
        node_tree_id, node_parent_id, node_level) = connection.execute(
        select([table.c.lft, table.c.rgt,
                table.c.tree_id, table.c.parent_id, table.c.level])
        .where(table.c.id == node_id)
    ).fetchone()

    """ Put there id of new parent node (there moving node should be moved)
        put there right position of new parent node (there moving node should
        be moved)
    """
    (parent_id, parent_pos_right,
        parent_pos_left, parent_tree_id, parent_level) = connection.execute(
        select([table.c.id, table.c.rgt, table.c.lft, table.c.tree_id,
                table.c.level])
        .where(table.c.id == instance.parent_id)
    ).fetchone()

    # 'size' of moving node (including all it's sub nodes)
    node_size = node_pos_right - node_pos_left + 1

    """ insert subtree in exist tree
    """
    instance.tree_id = parent_tree_id
    _insert_subtree(table, connection, node_size,
                    node_pos_left, node_pos_right, parent_pos_left,
                    parent_pos_right, subtree,
                    parent_tree_id, parent_level, node_level)
