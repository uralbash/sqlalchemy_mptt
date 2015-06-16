from sqlalchemy.exc import IntegrityError


class Initialize(object):

    def test_tree_orm_initialize(self):
        t0 = self.model(ppk=30)
        t1 = self.model(ppk=31, parent=t0)
        t2 = self.model(ppk=32, parent=t1)
        t3 = self.model(ppk=33, parent=t1)

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

        t0 = self.model(ppk=40)
        t1 = self.model(ppk=41, parent=t0)
        t2 = self.model(ppk=42, parent=t1)
        t3 = self.model(ppk=43, parent=t2)
        t4 = self.model(ppk=44, parent=t3)
        t5 = self.model(ppk=45, parent=t4)

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
        transient_node = self.model(ppk=1, parent=None)
        self.session.add(transient_node)
        try:
            self.session.flush()
        except IntegrityError:
            pass
        self.session.rollback()
        self.session.add(self.model(ppk=46, parent=None))
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
        #                 id lft rgt lvl parent tree
        self.assertEqual([(1,   1, 22, 1, None, 1),
                          (2,   2,  5, 2,  1, 1),
                          (3,   3,  4, 3,  2, 1),
                          (4,   6, 11, 2,  1, 1),
                          (5,   7,  8, 3,  4, 1),
                          (6,   9, 10, 3,  4, 1),
                          (7,  12, 21, 2,  1, 1),
                          (8,  13, 16, 3,  7, 1),
                          (9,  14, 15, 4,  8, 1),
                          (10, 17, 20, 3,  7, 1),
                          (11, 18, 19, 4, 10, 1),

                          (12,  1, 22, 1, None, 2),
                          (13,  2,  5, 2, 12, 2),
                          (14,  3,  4, 3, 13, 2),
                          (15,  6, 11, 2, 12, 2),
                          (16,  7,  8, 3, 15, 2),
                          (17,  9, 10, 3, 15, 2),
                          (18, 12, 21, 2, 12, 2),
                          (19, 13, 16, 3, 18, 2),
                          (20, 14, 15, 4, 19, 2),
                          (21, 17, 20, 3, 18, 2),
                          (22, 18, 19, 4, 21, 2)], self.result.all())
