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


class NestedSetsExtension(object):

    @classmethod
    def mptt_before_insert(self, mapper, connection, instance):
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

    @classmethod
    def mptt_after_delete(self, mapper, connection, instance, delete=True):

        table = mapper.mapped_table
        lft = instance.left
        rgt = instance.right
        tree_id = instance.tree_id
        delta = rgt - lft + 1

        """ Delete node or baranch of node

            DELETE FROM tree WHERE lft >= $lft AND rgt <= $rgt
        """
        if delete:
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

    @classmethod
    def mptt_before_update(self, mapper, connection, instance):
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
         node_tree_id, node_parent_id) = connection.execute(
            select([table.c.lft, table.c.rgt,
                    table.c.tree_id, table.c.parent_id])
            .where(table.c.id == node_id)
        ).fetchone()

        # put there id of new parent node (there moving node should be moved)
        # put there right position of new parent node (there moving node should be moved)
        (parent_id, parent_pos_right,
         parent_pos_left, parent_tree_id) = connection.execute(
            select([table.c.id, table.c.rgt, table.c.lft, table.c.tree_id])
            .where(table.c.id == instance.parent_id)
        ).fetchone()

        # 'size' of moving node (including all it's sub nodes)
        node_size = node_pos_right - node_pos_left + 1

        if node_tree_id == parent_tree_id:
            """ If move node in current tree
            """
            self._update_tree(table, connection, node_id, node_size,
                              node_pos_left, node_pos_right, parent_pos_right,
                              node_tree_id)
        elif node_tree_id != parent_tree_id:
            """ If move node to another tree

                get subtree from node

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

            # new parent right
            delta = node_size * 2 + node_pos_left

            """ delete from old tree
            """
            self.mptt_after_delete(mapper, connection, instance, False)

            """ insert subtree in exist tree
            """
            instance.tree_id = parent_tree_id
            instance.right = delta
            self._insert_subtree(table, connection, node_id, node_size,
                                 node_pos_left, node_pos_right, parent_pos_left,
                                 parent_pos_right, node_tree_id, subtree,
                                 parent_tree_id, delta, instance, mapper)

    @classmethod
    def _insert_subtree(self, table, connection, node_id, node_size,
                        node_pos_left, node_pos_right, parent_pos_left,
                        parent_pos_right, node_tree_id, subtree,
                        parent_tree_id, delta, instance, mapper):
        """ step 1: rebuild inserted subtree
        """
        connection.execute(
            table.update(table.c.id.in_(subtree))
            .values(
                lft=table.c.lft-node_pos_left+parent_pos_left+1,
                rgt=table.c.rgt-node_pos_right+delta,
                tree_id=parent_tree_id
            )
        )

        """ step 2: update key of right side
        connection.execute(
            table.update(
                and_(table.c.rgt >= parent_pos_right,
                     table.c.id.notin_(subtree),
                     table.c.tree_id == parent_tree_id)
            ).values(
                rgt=case(
                    [(table.c.rgt >= parent_pos_right,
                        table.c.rgt + node_size)],
                    else_=table.c.rgt
                )
            )
        )
        """

    @classmethod
    def _update_tree(self, table, connection, node_id, node_size, node_pos_left,
                     node_pos_right, parent_pos_right, node_tree_id):
        """ step 1: temporary "remove" moving node

            UPDATE `list_items`
            SET `pos_left` = 0-(`pos_left`), `pos_right` = 0-(`pos_right`)
            WHERE `pos_left` >= @node_pos_left AND `pos_right` <= @node_pos_right;
        """
        connection.execute(
            table.update(
                and_(table.c.lft >= node_pos_left,
                     table.c.rgt <= node_pos_right,
                     table.c.tree_id == node_tree_id))
            .values(
                lft=0-table.c.lft,
                rgt=0-table.c.rgt,
            )
        )

        """ step 2: decrease left and/or right position values of currently
            'lower' items (and parents)

            UPDATE `list_items`
            SET `pos_left` = `pos_left` - @node_size
            WHERE `pos_left` > @node_pos_right;

            UPDATE `list_items`
            SET `pos_right` = `pos_right` - @node_size
            WHERE `pos_right` > @node_pos_right;
        """
        connection.execute(
            table.update(and_(table.c.lft > node_pos_right,
                         table.c.tree_id == node_tree_id))
            .values(lft=table.c.lft-node_size)
        )
        connection.execute(
            table.update(and_(table.c.rgt > node_pos_right,
                         table.c.tree_id == node_tree_id))
            .values(rgt=table.c.rgt-node_size)
        )

        """ step 3: increase left and/or right position values of future
            'lower' items (and parents)

            UPDATE `list_items`
            SET `pos_left` = `pos_left` + @node_size
            WHERE `pos_left` >= IF(@parent_pos_right > @node_pos_right,
                        @parent_pos_right - @node_size, @parent_pos_right);
        """
        clause = parent_pos_right
        if parent_pos_right > node_pos_right:
            clause = parent_pos_right - node_size

        connection.execute(
            table.update(and_(table.c.lft >= clause,
                         table.c.tree_id == node_tree_id))
            .values(lft=table.c.lft+node_size)
        )
        """
            UPDATE `list_items`
            SET `pos_right` = `pos_right` + @node_size
            WHERE `pos_right` >= IF(@parent_pos_right > @node_pos_right,
                        @parent_pos_right - @node_size, @parent_pos_right);
        """
        connection.execute(
            table.update(and_(table.c.rgt >= clause,
                         table.c.tree_id == node_tree_id))
            .values(rgt=table.c.rgt+node_size)
        )

        """ step 4: move node (ant it's subnodes) and update it's parent item id

            UPDATE `list_items`
            SET
                `pos_left` = 0-(`pos_left`)+IF(@parent_pos_right > @node_pos_right,
                                               @parent_pos_right - @node_pos_right - 1,
                                               @parent_pos_right - @node_pos_right - 1 + @node_size),
                `pos_right` = 0-(`pos_right`)+IF(@parent_pos_right > @node_pos_right,
                                                 @parent_pos_right - @node_pos_right - 1,
                                                 @parent_pos_right - @node_pos_right - 1 + @node_size)
            WHERE `pos_left` <= 0-@node_pos_left AND `pos_right` >= 0-@node_pos_right;
        """
        clause = parent_pos_right - node_pos_right - 1 + node_size
        if parent_pos_right > node_pos_right:
            clause = parent_pos_right - node_pos_right - 1

        connection.execute(
            table.update(and_(table.c.lft <= 0-node_pos_left,
                              table.c.rgt >= 0-node_pos_right,
                              table.c.tree_id == node_tree_id))
            .values(lft=0-table.c.lft+clause,
                    rgt=0-table.c.rgt+clause)
        )
