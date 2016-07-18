class Changes(object):

    def test_update_wo_move(self):
        """ Update node w/o move
        initial state of the tree :mod:`sqlalchemy_mptt.tests.add_mptt_tree`
        .. code::
            level           Nested sets example
            1                    1(1)22
                    _______________|___________________
                   |               |                   |
            2    2(2)5           6(4)11             12(7)21
                   |               ^                   ^
            3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                                  |          |
            4                                  14(9)15   18(11)19
        """
        node = self.session.query(self.model)\
            .filter(self.model.get_pk_column() == 4).one()
        node.visible = True

        node2 = self.session.query(self.model)\
            .filter(self.model.get_pk_column() == 12).one()

        self.session.add(node)
        #                 id lft rgt lvl parent tree
        self.assertEqual(
            [(1,   1, 22, 1, None, node.tree_id),
             (2,   2,  5, 2,  1, node.tree_id),
             (3,   3,  4, 3,  2, node.tree_id),
             (4,   6, 11, 2,  1, node.tree_id),
             (5,   7,  8, 3,  4, node.tree_id),
             (6,   9, 10, 3,  4, node.tree_id),
             (7,  12, 21, 2,  1, node.tree_id),
             (8,  13, 16, 3,  7, node.tree_id),
             (9,  14, 15, 4,  8, node.tree_id),
             (10, 17, 20, 3,  7, node.tree_id),
             (11, 18, 19, 4, 10, node.tree_id),

             (12,  1, 22, 1, None, node2.tree_id),
             (13,  2,  5, 2, 12, node2.tree_id),
             (14,  3,  4, 3, 13, node2.tree_id),
             (15,  6, 11, 2, 12, node2.tree_id),
             (16,  7,  8, 3, 15, node2.tree_id),
             (17,  9, 10, 3, 15, node2.tree_id),
             (18, 12, 21, 2, 12, node2.tree_id),
             (19, 13, 16, 3, 18, node2.tree_id),
             (20, 14, 15, 4, 19, node2.tree_id),
             (21, 17, 20, 3, 18, node2.tree_id),
             (22, 18, 19, 4, 21, node2.tree_id)], self.result.all())  # flake8: noqa

    def test_update_wo_move_like_sacrud_save(self):
        """ Just change attr from node w/o move
        initial state of the tree :mod:`sqlalchemy_mptt.tests.add_mptt_tree`
        .. code::
            level           Nested sets example
            1                    1(1)22
                    _______________|___________________
                   |               |                   |
            2    2(2)5           6(4)11             12(7)21
                   |               ^                   ^
            3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                                  |          |
            4                                  14(9)15   18(11)19
        """
        node = self.session.query(self.model)\
            .filter(self.model.get_pk_column() == 4).one()
        node.parent_id = '1'
        node.visible = True

        node2 = self.session.query(self.model) \
            .filter(self.model.get_pk_column() == 12).one()

        self.session.add(node)
        #                 id lft rgt lvl parent tree
        self.assertEqual([(1,   1, 22, 1, None, node.tree_id),
                          (2,   2,  5, 2,  1, node.tree_id),
                          (3,   3,  4, 3,  2, node.tree_id),
                          (4,   6, 11, 2,  1, node.tree_id),
                          (5,   7,  8, 3,  4, node.tree_id),
                          (6,   9, 10, 3,  4, node.tree_id),
                          (7,  12, 21, 2,  1, node.tree_id),
                          (8,  13, 16, 3,  7, node.tree_id),
                          (9,  14, 15, 4,  8, node.tree_id),
                          (10, 17, 20, 3,  7, node.tree_id),
                          (11, 18, 19, 4, 10, node.tree_id),

                          (12,  1, 22, 1, None, node2.tree_id),
                          (13,  2,  5, 2, 12, node2.tree_id),
                          (14,  3,  4, 3, 13, node2.tree_id),
                          (15,  6, 11, 2, 12, node2.tree_id),
                          (16,  7,  8, 3, 15, node2.tree_id),
                          (17,  9, 10, 3, 15, node2.tree_id),
                          (18, 12, 21, 2, 12, node2.tree_id),
                          (19, 13, 16, 3, 18, node2.tree_id),
                          (20, 14, 15, 4, 19, node2.tree_id),
                          (21, 17, 20, 3, 18, node2.tree_id),
                          (22, 18, 19, 4, 21, node2.tree_id)], self.result.all())

    def test_insert_node(self):
        """ Insert node with parent==6
        initial state of the tree :mod:`sqlalchemy_mptt.tests.add_mptt_tree`
        .. code::
            level           Nested sets example
            1                    1(1)22
                    _______________|___________________
                   |               |                   |
            2    2(2)5           6(4)11             12(7)21
                   |               ^                   ^
            3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                                  |          |
            4                                  14(9)15   18(11)19
            level     Insert node with parent_id == 6
            1                    1(1)24
                    _______________|_________________
                   |               |                 |
            2    2(2)5           6(4)13           14(7)23
                   |           ____|____          ___|____
                   |          |         |        |        |
            3    3(3)4      7(5)8    9(6)12  15(8)18   19(10)22
                                       |        |         |
            4                      10(23)11  16(9)17  20(11)21
        """
        node = self.model(parent_id=6)
        self.session.add(node)
        node1 = self.session.query(self.model) \
            .filter(self.model.get_pk_column() == 1).one()
        node12 = self.session.query(self.model) \
            .filter(self.model.get_pk_column() == 12).one()
        #                 id lft rgt lvl parent tree
        self.assertEqual([(1,   1, 24, 1, None, node1.tree_id),
                          (2,   2,  5, 2,  1, node1.tree_id),
                          (3,   3,  4, 3,  2, node1.tree_id),
                          (4,   6, 13, 2,  1, node1.tree_id),
                          (5,   7,  8, 3,  4, node1.tree_id),
                          (6,   9, 12, 3,  4, node1.tree_id),
                          (7,  14, 23, 2,  1, node1.tree_id),
                          (8,  15, 18, 3,  7, node1.tree_id),
                          (9,  16, 17, 4,  8, node1.tree_id),
                          (10, 19, 22, 3,  7, node1.tree_id),
                          (11, 20, 21, 4, 10, node1.tree_id),

                          (12,  1, 22, 1, None, node12.tree_id),
                          (13,  2,  5, 2, 12, node12.tree_id),
                          (14,  3,  4, 3, 13, node12.tree_id),
                          (15,  6, 11, 2, 12, node12.tree_id),
                          (16,  7,  8, 3, 15, node12.tree_id),
                          (17,  9, 10, 3, 15, node12.tree_id),
                          (18, 12, 21, 2, 12, node12.tree_id),
                          (19, 13, 16, 3, 18, node12.tree_id),
                          (20, 14, 15, 4, 19, node12.tree_id),
                          (21, 17, 20, 3, 18, node12.tree_id),
                          (22, 18, 19, 4, 21, node12.tree_id),

                          (23, 10, 11, 4, 6, node.tree_id)], self.result.all())

    def test_insert_node_near_subtree(self):
        """ Insert node with parent==4
        initial state of the tree :mod:`sqlalchemy_mptt.tests.add_mptt_tree`
        .. code::
            level           Nested sets example
            1                    1(1)22
                    _______________|___________________
                   |               |                   |
            2    2(2)5           6(4)11             12(7)21
                   |               ^                   ^
            3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                                  |          |
            4                                  14(9)15   18(11)19
            level     Insert node with parent_id == 4
            1                    1(1)24
                    _______________|_____________________
                   |               |                     |
            2    2(2)5           6(4)13               14(7)23
                   |         ______|________           __|______
                   |        |      |        |         |         |
            3    3(3)4    7(5)8  9(6)10  11(23)12  15(8)18   19(10)22
                                                      |         |
            4                                      16(9)17   20(11)21
        """
        node = self.model(parent_id=4)
        self.session.add(node)
        node1 = self.session.query(self.model) \
            .filter(self.model.get_pk_column() == 1).one()
        node12 = self.session.query(self.model) \
            .filter(self.model.get_pk_column() == 12).one()
        #                 id lft rgt lvl parent tree
        self.assertEqual([(1,   1, 24, 1, None, node1.tree_id),
                          (2,   2,  5, 2,  1, node1.tree_id),
                          (3,   3,  4, 3,  2, node1.tree_id),
                          (4,   6, 13, 2,  1, node1.tree_id),
                          (5,   7,  8, 3,  4, node1.tree_id),
                          (6,   9, 10, 3,  4, node1.tree_id),
                          (7,  14, 23, 2,  1, node1.tree_id),
                          (8,  15, 18, 3,  7, node1.tree_id),
                          (9,  16, 17, 4,  8, node1.tree_id),
                          (10, 19, 22, 3,  7, node1.tree_id),
                          (11, 20, 21, 4, 10, node1.tree_id),

                          (12,  1, 22, 1, None, node12.tree_id),
                          (13,  2,  5, 2, 12, node12.tree_id),
                          (14,  3,  4, 3, 13, node12.tree_id),
                          (15,  6, 11, 2, 12, node12.tree_id),
                          (16,  7,  8, 3, 15, node12.tree_id),
                          (17,  9, 10, 3, 15, node12.tree_id),
                          (18, 12, 21, 2, 12, node12.tree_id),
                          (19, 13, 16, 3, 18, node12.tree_id),
                          (20, 14, 15, 4, 19, node12.tree_id),
                          (21, 17, 20, 3, 18, node12.tree_id),
                          (22, 18, 19, 4, 21, node12.tree_id),

                          (23, 11, 12, 3,  4, node.tree_id)], self.result.all())

    def test_insert_after_node(self):
        pass

    def test_delete_node(self):
        """ Delete node(4)
        initial state of the tree :mod:`sqlalchemy_mptt.tests.add_mptt_tree`
        .. code::
            level           Test delete node
            1                    1(1)22
                    _______________|___________________
                   |               |                   |
            2    2(2)5           6(4)11             12(7)21
                   |               ^                   ^
            3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                                  |          |
            4                                  14(9)15   18(11)19
            level         Delete node == 4
            1                    1(1)16
                    _______________|_____
                   |                     |
            2    2(2)5                 6(7)15
                   |                     ^
            3    3(3)4            7(8)10   11(10)14
                                    |          |
            4                     8(9)9    12(11)13
        """
        node = self.session.query(self.model)\
            .filter(self.model.get_pk_column() == 4).one()
        node2 = self.session.query(self.model) \
            .filter(self.model.get_pk_column() == 12).one()
        self.session.delete(node)
        #                 id lft rgt lvl parent tree
        self.assertEqual([(1,   1, 16, 1, None, node.tree_id),
                          (2,   2,  5, 2,  1, node.tree_id),
                          (3,   3,  4, 3,  2, node.tree_id),
                          (7,   6, 15, 2,  1, node.tree_id),
                          (8,   7, 10, 3,  7, node.tree_id),
                          (9,   8,  9, 4,  8, node.tree_id),
                          (10, 11, 14, 3,  7, node.tree_id),
                          (11, 12, 13, 4, 10, node.tree_id),

                          (12,  1, 22, 1, None, node2.tree_id),
                          (13,  2,  5, 2, 12, node2.tree_id),
                          (14,  3,  4, 3, 13, node2.tree_id),
                          (15,  6, 11, 2, 12, node2.tree_id),
                          (16,  7,  8, 3, 15, node2.tree_id),
                          (17,  9, 10, 3, 15, node2.tree_id),
                          (18, 12, 21, 2, 12, node2.tree_id),
                          (19, 13, 16, 3, 18, node2.tree_id),
                          (20, 14, 15, 4, 19, node2.tree_id),
                          (21, 17, 20, 3, 18, node2.tree_id),
                          (22, 18, 19, 4, 21, node2.tree_id)], self.result.all())

    def test_update_node(self):
        """ Set parent_id==5 for node(8)
        initial state of the tree :mod:`sqlalchemy_mptt.tests.add_mptt_tree`
        .. code::
            level           Test update node
                1                    1(1)22
                        _______________|___________________
                       |               |                   |
                2    2(2)5           6(4)11             12(7)21
                       |               ^                   ^
                3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                                      |          |
                4                                  14(9)15   18(11)19
            level               Move 8 - > 5
                1                     1(1)22
                         _______________|__________________
                        |               |                  |
                2     2(2)5           6(4)15            16(7)21
                        |               ^                  |
                3     3(3)4      7(5)12   13(6)14      17(10)20
                                   |                        |
                4                8(8)11                18(11)19
                                   |
                5                9(9)10
        """
        node = self.session.query(self.model)\
            .filter(self.model.get_pk_column() == 8).one()
        node.parent_id = 5
        self.session.add(node)

        node1 = self.session.query(self.model) \
            .filter(self.model.get_pk_column() == 1).one()
        node12 = self.session.query(self.model) \
            .filter(self.model.get_pk_column() == 12).one()
        #                 id lft rgt lvl parent tree
        self.assertEqual([(1, 1, 22, 1, None, node1.tree_id),
                          (2,   2,  5, 2,  1, node1.tree_id),
                          (3,   3,  4, 3,  2, node1.tree_id),
                          (4,   6, 15, 2,  1, node1.tree_id),
                          (5,   7, 12, 3,  4, node1.tree_id),
                          (6,  13, 14, 3,  4, node1.tree_id),
                          (7,  16, 21, 2,  1, node1.tree_id),
                          (8,   8, 11, 4,  5, node1.tree_id),
                          (9,   9, 10, 5,  8, node1.tree_id),
                          (10, 17, 20, 3,  7, node1.tree_id),
                          (11, 18, 19, 4, 10, node1.tree_id),

                          (12,  1, 22, 1, None, node12.tree_id),
                          (13,  2,  5, 2, 12, node12.tree_id),
                          (14,  3,  4, 3, 13, node12.tree_id),
                          (15,  6, 11, 2, 12, node12.tree_id),
                          (16,  7,  8, 3, 15, node12.tree_id),
                          (17,  9, 10, 3, 15, node12.tree_id),
                          (18, 12, 21, 2, 12, node12.tree_id),
                          (19, 13, 16, 3, 18, node12.tree_id),
                          (20, 14, 15, 4, 19, node12.tree_id),
                          (21, 17, 20, 3, 18, node12.tree_id),
                          (22, 18, 19, 4, 21, node12.tree_id)], self.result.all())

        """ level               Move 8 - > 5
                1                     1(1)22
                         _______________|__________________
                        |               |                  |
                2     2(2)5           6(4)15            16(7)21
                        |               ^                  |
                3     3(3)4      7(5)12   13(6)14      17(10)20
                                   |                        |
                4                8(8)11                18(11)19
                                   |
                5                9(9)10
            level               Move 4 - > 2
                1                     1(1)22
                                ________|_____________
                               |                      |
                2            2(2)15                16(7)21
                           ____|_____                 |
                          |          |                |
                3       3(4)12    13(3)14         17(10)20
                          ^                           |
                4  4(5)9    10(6)11               18(11)19
                     |
                5  5(8)8
                     |
                6  6(9)7
        """
        node4 = self.session.query(self.model)\
            .filter(self.model.get_pk_column() == 4).one()
        node4.parent_id = 2
        self.session.add(node4)
        node2 = self.session.query(self.model) \
            .filter(self.model.get_pk_column() == 12).one()
        node1 = self.session.query(self.model) \
            .filter(self.model.get_pk_column() == 1).one()
        #                 id lft rgt lvl parent tree
        self.assertEqual([(1,   1, 22, 1, None, node1.tree_id),
                          (2,   2, 15, 2,  1, node1.tree_id),
                          (3,  13, 14, 3,  2, node1.tree_id),
                          (4,   3, 12, 3,  2, node1.tree_id),
                          (5,   4,  9, 4,  4, node1.tree_id),
                          (6,  10, 11, 4,  4, node1.tree_id),
                          (7,  16, 21, 2,  1, node1.tree_id),
                          (8,   5,  8, 5,  5, node1.tree_id),
                          (9,   6,  7, 6,  8, node1.tree_id),
                          (10, 17, 20, 3,  7, node1.tree_id),
                          (11, 18, 19, 4, 10, node1.tree_id),

                          (12,  1, 22, 1, None, node2.tree_id),
                          (13,  2,  5, 2, 12, node2.tree_id),
                          (14,  3,  4, 3, 13, node2.tree_id),
                          (15,  6, 11, 2, 12, node2.tree_id),
                          (16,  7,  8, 3, 15, node2.tree_id),
                          (17,  9, 10, 3, 15, node2.tree_id),
                          (18, 12, 21, 2, 12, node2.tree_id),
                          (19, 13, 16, 3, 18, node2.tree_id),
                          (20, 14, 15, 4, 19, node2.tree_id),
                          (21, 17, 20, 3, 18, node2.tree_id),
                          (22, 18, 19, 4, 21, node2.tree_id)], self.result.all())

        """ level               Move 4 - > 2
                1                     1(1)22
                                ________|_____________
                               |                      |
                2            2(2)15                16(7)21
                           ____|_____                 |
                          |          |                |
                3       3(4)12    13(3)14         17(10)20
                          ^                           |
                4   4(5)9   10(6)11               18(11)19
                      |
                5   5(8)8
                      |
                6   6(9)7
            level               Move 8 - > 10
                1                     1(1)22
                                ________|_____________
                               |                      |
                2            2(2)11                12(7)21
                         ______|_____                 |
                        |            |                |
                3     3(4)8        9(3)10         13(10)20
                      __|____                        _|______
                     |       |                      |        |
                4  4(5)5   6(6)7                 14(8)17  18(11)19
                                                    |
                5                                15(9)16
        """

        node8 = self.session.query(self.model)\
            .filter(self.model.get_pk_column() == 8).one()
        node8.parent_id = 10
        self.session.add(node8)

        node1 = self.session.query(self.model) \
            .filter(self.model.get_pk_column() == 1).one()
        node12 = self.session.query(self.model) \
            .filter(self.model.get_pk_column() == 12).one()
        #                 id lft rgt lvl parent tree
        self.assertEqual([(1,   1, 22, 1, None, node1.tree_id),
                          (2,   2, 11, 2,  1, node1.tree_id),
                          (3,   9, 10, 3,  2, node1.tree_id),
                          (4,   3,  8, 3,  2, node1.tree_id),
                          (5,   4,  5, 4,  4, node1.tree_id),
                          (6,   6,  7, 4,  4, node1.tree_id),
                          (7,  12, 21, 2,  1, node1.tree_id),
                          (8,  14, 17, 4, 10, node1.tree_id),
                          (9,  15, 16, 5,  8, node1.tree_id),
                          (10, 13, 20, 3,  7, node1.tree_id),
                          (11, 18, 19, 4, 10, node1.tree_id),

                          (12,  1, 22, 1, None, node12.tree_id),
                          (13,  2,  5, 2, 12, node12.tree_id),
                          (14,  3,  4, 3, 13, node12.tree_id),
                          (15,  6, 11, 2, 12, node12.tree_id),
                          (16,  7,  8, 3, 15, node12.tree_id),
                          (17,  9, 10, 3, 15, node12.tree_id),
                          (18, 12, 21, 2, 12, node12.tree_id),
                          (19, 13, 16, 3, 18, node12.tree_id),
                          (20, 14, 15, 4, 19, node12.tree_id),
                          (21, 17, 20, 3, 18, node12.tree_id),
                          (22, 18, 19, 4, 21, node12.tree_id)], self.result.all())

    def test_rebuild(self):
        """ Rebuild tree with tree_id==1

        .. code::

            level      Nested sets w/o left & right (or broken left & right)
                1                     (1)
                        _______________|___________________
                       |               |                   |
                2     (2)             (4)                 (7)
                       |               ^                   ^
                3     (3)          (5)   (6)           (8)   (10)
                                                        |      |
                4                                      (9)   (11)


                level           Nested sets after rebuild
                1                    1(1)22
                        _______________|___________________
                       |               |                   |
                2    2(2)5           6(4)11             12(7)21
                       |               ^                   ^
                3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                                      |          |
                4                                  14(9)15   18(11)19
        """

        self.session.query(self.model).update({
            self.model.left: 0,
            self.model.right: 0,
            self.model.level: 0
        })
        node1 = self.session.query(self.model)\
            .filter(self.model.get_pk_column() == 1).one()
        node2 = self.session.query(self.model) \
            .filter(self.model.get_pk_column() == 12).one()
        self.model.rebuild(self.session, node1.tree_id)
        #                 id lft rgt lvl parent tree
        self.assertEqual(self.result.all(),
                         [(1,   1, 22, 1, None, node1.tree_id),
                          (2,   2,  5, 2, 1,  node1.tree_id),
                          (3,   3,  4, 3, 2,  node1.tree_id),
                          (4,   6, 11, 2, 1,  node1.tree_id),
                          (5,   7,  8, 3, 4,  node1.tree_id),
                          (6,   9, 10, 3, 4,  node1.tree_id),
                          (7,  12, 21, 2, 1,  node1.tree_id),
                          (8,  13, 16, 3, 7,  node1.tree_id),
                          (9,  14, 15, 4, 8,  node1.tree_id),
                          (10, 17, 20, 3, 7,  node1.tree_id),
                          (11, 18, 19, 4, 10, node1.tree_id),

                          (12, 0, 0, 0, None, node2.tree_id),
                          (13, 0, 0, 0, 12, node2.tree_id),
                          (14, 0, 0, 0, 13, node2.tree_id),
                          (15, 0, 0, 0, 12, node2.tree_id),
                          (16, 0, 0, 0, 15, node2.tree_id),
                          (17, 0, 0, 0, 15, node2.tree_id),
                          (18, 0, 0, 0, 12, node2.tree_id),
                          (19, 0, 0, 0, 18, node2.tree_id),
                          (20, 0, 0, 0, 19, node2.tree_id),
                          (21, 0, 0, 0, 18, node2.tree_id),
                          (22, 0, 0, 0, 21, node2.tree_id)])

        self.model.rebuild(self.session)
        #                 id lft rgt lvl parent tree
        self.assertEqual(self.result.all(),
                         [(1,   1, 22, 1, None, node1.tree_id),
                          (2,   2,  5, 2, 1,  node1.tree_id),
                          (3,   3,  4, 3, 2,  node1.tree_id),
                          (4,   6, 11, 2, 1,  node1.tree_id),
                          (5,   7,  8, 3, 4,  node1.tree_id),
                          (6,   9, 10, 3, 4,  node1.tree_id),
                          (7,  12, 21, 2, 1,  node1.tree_id),
                          (8,  13, 16, 3, 7,  node1.tree_id),
                          (9,  14, 15, 4, 8,  node1.tree_id),
                          (10, 17, 20, 3, 7,  node1.tree_id),
                          (11, 18, 19, 4, 10, node1.tree_id),

                          (12,  1, 22, 1, None, node2.tree_id),
                          (13,  2,  5, 2, 12, node2.tree_id),
                          (14,  3,  4, 3, 13, node2.tree_id),
                          (15,  6, 11, 2, 12, node2.tree_id),
                          (16,  7,  8, 3, 15, node2.tree_id),
                          (17,  9, 10, 3, 15, node2.tree_id),
                          (18, 12, 21, 2, 12, node2.tree_id),
                          (19, 13, 16, 3, 18, node2.tree_id),
                          (20, 14, 15, 4, 19, node2.tree_id),
                          (21, 17, 20, 3, 18, node2.tree_id),
                          (22, 18, 19, 4, 21, node2.tree_id)])
