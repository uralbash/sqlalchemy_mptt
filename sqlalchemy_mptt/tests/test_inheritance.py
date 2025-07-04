import unittest

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from sqlalchemy_mptt.mixins import BaseNestedSets
from sqlalchemy_mptt.sqlalchemy_compat import compat_layer
from sqlalchemy_mptt.tests import TreeTestingMixin, failures_expected_on


Base = compat_layer.declarative_base()


class GenericTree(Base, BaseNestedSets):
    __tablename__ = "generic"

    ppk = sa.Column('idd', sa.Integer, primary_key=True)
    type = sa.Column(sa.Integer, default=0)
    visible = sa.Column(sa.Boolean)

    sqlalchemy_mptt_pk_name = 'ppk'

    __mapper_args__ = {
        'polymorphic_identity': 0,
        'polymorphic_on': type,
    }

    def __repr__(self):
        return "<Node (%s)>" % self.ppk


class SpecializedTree(GenericTree):
    __tablename__ = "specialized"

    ppk = sa.Column(
        'idd',
        sa.Integer,
        sa.ForeignKey(GenericTree.ppk),
        primary_key=True
    )

    __mapper_args__ = {
        'polymorphic_identity': 1,
    }
    __table_args__ = tuple()


class TestTree(unittest.TestCase):

    def setUp(self):
        self.engine = sa.create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_create_generic(self):
        self.session.add(GenericTree(ppk=1))
        self.session.commit()

        tree = compat_layer.get(self.session, GenericTree, 1)
        self.assertEqual(tree.ppk, 1)
        self.assertEqual(tree.tree_id, 1)

    def test_create_spec(self):
        self.session.add(SpecializedTree(ppk=1))
        self.session.commit()

        tree = compat_layer.get(self.session, SpecializedTree, 1)
        self.assertEqual(tree.ppk, 1)
        self.assertEqual(tree.tree_id, 1)

    def test_create_delete(self):
        parent = SpecializedTree(ppk=1)

        child1 = SpecializedTree(ppk=2, parent=parent)
        child2 = GenericTree(ppk=3, parent=parent)

        GenericTree(ppk=4, parent=child2)
        SpecializedTree(ppk=5, parent=child2)

        self.session.add(parent)
        self.session.commit()

        tree = compat_layer.get(self.session, SpecializedTree, 1)
        self.assertEqual(tree.ppk, 1)
        self.assertEqual(tree.tree_id, 1)

        self.session.delete(child1)
        self.session.commit()

        self.assertEqual(None, compat_layer.get(self.session, SpecializedTree, 2))

        self.session.delete(child2)
        self.session.commit()

        self.assertEqual(None, compat_layer.get(self.session, SpecializedTree, 3))
        self.assertEqual(None, compat_layer.get(self.session, SpecializedTree, 4))
        self.assertEqual(None, compat_layer.get(self.session, SpecializedTree, 5))


class TestGenericTree(TreeTestingMixin, unittest.TestCase):
    base = Base
    model = GenericTree


class TestSpecializedTree(TreeTestingMixin, unittest.TestCase):
    base = Base
    model = SpecializedTree

    @unittest.expectedFailure
    def test_rebuild(self):
        # This test will always fail on specialized classes.
        super().test_rebuild()


Base2 = compat_layer.declarative_base()


class BaseInheritance(Base2):
    __tablename__ = "base_inheritance"

    ppk = sa.Column('idd', sa.Integer, primary_key=True)
    type = sa.Column(sa.Integer, default=0)
    visible = sa.Column(sa.Boolean)

    __mapper_args__ = {
        'polymorphic_identity': 0,
        'polymorphic_on': type,
    }

    def __repr__(self):
        return "<Node (%s)>" % self.ppk


class InheritanceTree(BaseInheritance, BaseNestedSets):
    __tablename__ = "inheriance_tree"

    ppk = sa.Column('idd', sa.Integer, sa.ForeignKey(BaseInheritance.ppk),
                    primary_key=True)
    sqlalchemy_mptt_pk_name = 'ppk'

    __mapper_args__ = {
        'polymorphic_identity': 1,
    }


class TestInheritanceTree(TreeTestingMixin, unittest.TestCase):
    base = Base2
    model = InheritanceTree

    @failures_expected_on(sqlalchemy_versions=['1.0', '1.1', '1.2', '1.3'])
    def test_rebuild(self):
        super().test_rebuild()
