from sqlalchemy.exc import IntegrityError


class Initialize(object):

    def test_tree_orm_initialize(self):
        pk_name = self.model.get_pk_name()
        t0 = self.model(**{pk_name: 30})
        t1 = self.model(**{pk_name: 31, 'parent': t0})
        t2 = self.model(**{pk_name: 32, 'parent': t1})
        t3 = self.model(**{pk_name: 33, 'parent': t1})

        self.session.add(t0)
        self.session.flush()

        self.assertEqual(t0.left, 1)
        self.assertEqual(t0.right, 8)

        self.assertEqual(t1.left, 2)
        self.assertEqual(t1.right, 7)

        self.assertEqual(t2.left, 3)
        self.assertEqual(t2.right, 4)

        self.assertEqual(t3.left, 5)
        self.assertEqual(t3.right, 6)

        t0 = self.model(**{pk_name: 40})
        t1 = self.model(**{pk_name: 41, 'parent': t0})
        t2 = self.model(**{pk_name: 42, 'parent': t1})
        t3 = self.model(**{pk_name: 43, 'parent': t2})
        t4 = self.model(**{pk_name: 44, 'parent': t3})
        t5 = self.model(**{pk_name: 45, 'parent': t4})

        self.session.add(t3)
        self.session.flush()

        self.assertEqual(t0.left, 1)
        self.assertEqual(t0.right, 12)

        self.assertEqual(t1.left, 2)
        self.assertEqual(t1.right, 11)

        self.assertEqual(t2.left, 3)
        self.assertEqual(t2.right, 10)

        self.assertEqual(t3.left, 4)
        self.assertEqual(t3.right, 9)

        self.assertEqual(t4.left, 5)
        self.assertEqual(t4.right, 8)

        self.assertEqual(t5.left, 6)
        self.assertEqual(t5.right, 7)

    def test_flush_with_transient_nodes_present(self):
        """https://github.com/ITCase/sqlalchemy_mptt/issues/34"""
        pk_name = self.model.get_pk_name()
        transient_node = self.model(**{pk_name: 1, 'parent': None})
        self.session.add(transient_node)
        try:
            self.session.flush()
        except IntegrityError:
            pass
        self.session.rollback()
        self.session.add(self.model(**{pk_name: 46, 'parent': None}))
        self.session.flush()

    def test_tree_initialize(self):
        """ Initial state of the trees

        .. code::

            level               Tree 1
            1                    1(1)22
                    _______________|___________________
                   |               |                   |
            2    2(2)5           6(4)11             12(7)21
                   |               ^                   ^
            3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                                  |          |
            4                                  14(9)15   18(11)19


            level               Tree 2
            1                    1(12)22
                    _______________|___________________
                   |               |                   |
            2    2(13)5         6(15)11              12(18)21
                   |               ^                    ^
            3    3(14)4     7(16)8   9(17)10   13(19)16   17(21)20
                                                   |          |
            4                                  14(20)15   18(22)19

        """
        node1 = self.session.query(self.model) \
            .filter(self.model.get_pk_column() == 1).one()
        node2 = self.session.query(self.model) \
            .filter(self.model.get_pk_column() == 12).one()
        #    id lft rgt lvl parent tree
        self.assertEqual(
            [(1,   1, 22, 1, None, node1.tree_id),
             (2,   2,  5, 2,  1, node1.tree_id),
             (3,   3,  4, 3,  2, node1.tree_id),
             (4,   6, 11, 2,  1, node1.tree_id),
             (5,   7,  8, 3,  4, node1.tree_id),
             (6,   9, 10, 3,  4, node1.tree_id),
             (7,  12, 21, 2,  1, node1.tree_id),
             (8,  13, 16, 3,  7, node1.tree_id),
             (9,  14, 15, 4,  8, node1.tree_id),
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
             (22, 18, 19, 4, 21, node2.tree_id)], self.result.all())  # flake8: noqa
