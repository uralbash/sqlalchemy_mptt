def get_obj(session, model, id):
    return session.query(model).filter_by(ppk=id).one()


class Tree(object):

    def test_get_tree(self):
        """.. note::

            See [source] for full example

        Return tree as list of dict

        .. code::

            tree = Tree.get_tree(self.session)
        """
        tree = self.model.get_tree(self.session)

        def go(id):
            return get_obj(self.session, self.model, id)

        reference_tree = [{'node': go(1), 'children': [{'node': go(2), 'children': [{'node': go(3)}]}, {'node': go(4), 'children': [{'node': go(5)}, {'node': go(6)}]}, {'node': go(7), 'children': [{'node': go(8), 'children': [{'node': go(9)}]}, {'node': go(10), 'children': [{'node': go(11)}]}]}]}, {'node': go(12), 'children': [{'node': go(13), 'children': [{'node': go(14)}]}, {'node': go(15), 'children': [{'node': go(16)}, {'node': go(17)}]}, {'node': go(18), 'children': [{'node': go(19), 'children': [{'node': go(20)}]}, {'node': go(21), 'children': [{'node': go(22)}]}]}]}]  # noqa

        self.assertEqual(tree, reference_tree)

    def test_get_tree_count_query(self):
        """
        Count num of queries to the database.
        See https://github.com/ITCase/sqlalchemy_mptt/issues/39


        Use ``--nocapture`` option for show run time:

        ::

            nosetests sqlalchemy_mptt.tests.test_events:TestTree.test_get_tree_count_query --nocapture
            Get tree:             0:00:00.001817
            .
            ----------------------------------------------------------------------
            Ran 1 test in 0.064s

            OK
        """  # noqa
        from datetime import datetime
        self.session.commit()

        # Get tree by for cycle
        self.start_query_counter()
        self.assertEqual(0, len(self.stmts))
        startTime = datetime.now()
        self.model.get_tree(self.session)
        print("Get tree: {!s:>26}".format(datetime.now() - startTime))
        self.assertEqual(1, len(self.stmts))
        self.stop_query_counter()

    def test_get_json_tree(self):
        """.. note::

            See [source] for full example

        Return tree as JSON of jqTree format

        .. code::

            tree = Tree.get_tree(self.session, json=True)
        """
        reference_tree = [{'children': [{'children': [{'id': 3, 'label': '<Node (3)>'}], 'id': 2, 'label': '<Node (2)>'}, {'children': [{'id': 5, 'label': '<Node (5)>'}, {'id': 6, 'label': '<Node (6)>'}], 'id': 4, 'label': '<Node (4)>'}, {'children': [{'children': [{'id': 9, 'label': '<Node (9)>'}], 'id': 8, 'label': '<Node (8)>'}, {'children': [{'id': 11, 'label': '<Node (11)>'}], 'id': 10, 'label': '<Node (10)>'}], 'id': 7, 'label': '<Node (7)>'}], 'id': 1, 'label': '<Node (1)>'}, {'children': [{'children': [{'id': 14, 'label': '<Node (14)>'}], 'id': 13, 'label': '<Node (13)>'}, {'children': [{'id': 16, 'label': '<Node (16)>'}, {'id': 17, 'label': '<Node (17)>'}], 'id': 15, 'label': '<Node (15)>'}, {'children': [{'children': [{'id': 20, 'label': '<Node (20)>'}], 'id': 19, 'label': '<Node (19)>'}, {'children': [{'id': 22, 'label': '<Node (22)>'}], 'id': 21, 'label': '<Node (21)>'}], 'id': 18, 'label': '<Node (18)>'}], 'id': 12, 'label': '<Node (12)>'}]  # noqa

        tree = self.model.get_tree(self.session, json=True)
        self.assertEqual(tree, reference_tree)

    def test_get_json_tree_with_custom_field(self):
        """.. note::

            See [source] for full example

        Return tree as JSON of jqTree format with additional field

        .. code-block:: python
            :linenos:

            def fields(node):
                return {'visible': node.visible}

            tree = Tree.get_tree(self.session, json=True, json_fields=fields)
        """
        def fields(node):
            return {'visible': node.visible}

        reference_tree = [{'visible': None, 'children': [{'visible': True, 'children': [{'visible': True, 'id': 3, 'label': '<Node (3)>'}], 'id': 2, 'label': '<Node (2)>'}, {'visible': True, 'children': [{'visible': True, 'id': 5, 'label': '<Node (5)>'}, {'visible': True, 'id': 6, 'label': '<Node (6)>'}], 'id': 4, 'label': '<Node (4)>'}, {'visible': True, 'children': [{'visible': True, 'children': [{'visible': None, 'id': 9, 'label': '<Node (9)>'}], 'id': 8, 'label': '<Node (8)>'}, {'visible': None, 'children': [{'visible': None, 'id': 11, 'label': '<Node (11)>'}], 'id': 10, 'label': '<Node (10)>'}], 'id': 7, 'label': '<Node (7)>'}], 'id': 1, 'label': '<Node (1)>'}, {'visible': None, 'children': [{'visible': None, 'children': [{'visible': None, 'id': 14, 'label': '<Node (14)>'}], 'id': 13, 'label': '<Node (13)>'}, {'visible': None, 'children': [{'visible': None, 'id': 16, 'label': '<Node (16)>'}, {'visible': None, 'id': 17, 'label': '<Node (17)>'}], 'id': 15, 'label': '<Node (15)>'}, {'visible': None, 'children': [{'visible': None, 'children': [{'visible': None, 'id': 20, 'label': '<Node (20)>'}], 'id': 19, 'label': '<Node (19)>'}, {'visible': None, 'children': [{'visible': None, 'id': 22, 'label': '<Node (22)>'}], 'id': 21, 'label': '<Node (21)>'}], 'id': 18, 'label': '<Node (18)>'}], 'id': 12, 'label': '<Node (12)>'}]  # noqa

        tree = self.model.get_tree(self.session, json=True, json_fields=fields)
        self.assertEqual(tree, reference_tree)

    def test_leftsibling_in_level(self):
        """ Node to the left of the current node at the same level

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

            level1 = [1]
            level2 = [2, 4, 7]
            level3 = [3, 5, 6, 8, 10]
            level4 = [9, 11]

            leftsibling_in_level_of_node_3 = None
            leftsibling_in_level_of_node_5 = 3
            leftsibling_in_level_of_node_6 = 5
            leftsibling_in_level_of_node_8 = 6
            leftsibling_in_level_of_node_11 = 9
        """
        q = self.session.query(self.model)
        node3 = q.filter(self.model.ppk == 3).one()
        node5 = q.filter(self.model.ppk == 5).one()
        node6 = q.filter(self.model.ppk == 6).one()
        node8 = q.filter(self.model.ppk == 8).one()
        node10 = q.filter(self.model.ppk == 10).one()
        self.assertEqual(node10.leftsibling_in_level().idd, node8.ppk)
        self.assertEqual(node8.leftsibling_in_level().idd, node6.ppk)
        self.assertEqual(node6.leftsibling_in_level().idd, node5.ppk)
        self.assertEqual(node3.leftsibling_in_level(), None)
