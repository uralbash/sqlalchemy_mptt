import unittest

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from . import TreeTestingMixin
from ..mixins import BaseNestedSets

Base = declarative_base()


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

        tree = self.session.query(GenericTree).get(1)
        self.assertEqual(tree.ppk, 1)
        self.assertEqual(tree.tree_id, 1)

    def test_create_spec(self):
        self.session.add(SpecializedTree(ppk=1))
        self.session.commit()

        tree = self.session.query(SpecializedTree).get(1)
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

        tree = self.session.query(SpecializedTree).get(1)
        self.assertEqual(tree.ppk, 1)
        self.assertEqual(tree.tree_id, 1)

        self.session.delete(child1)
        self.session.commit()

        self.assertEquals(None, self.session.query(SpecializedTree).get(2))

        self.session.delete(child2)
        self.session.commit()

        self.assertEquals(None, self.session.query(SpecializedTree).get(3))
        self.assertEquals(None, self.session.query(SpecializedTree).get(4))
        self.assertEquals(None, self.session.query(SpecializedTree).get(5))


class TestGenericTree(TreeTestingMixin, unittest.TestCase):
    base = Base
    model = GenericTree


class TestSpecializedTree(TreeTestingMixin, unittest.TestCase):
    base = Base
    model = SpecializedTree

    def test_rebuild(self):
        # See the following URL for caveats when using update on mapped
        # hierarchies:
        # http://docs.sqlalchemy.org/en/rel_0_9/orm/query.html?highlight=update#sqlalchemy.orm.query.Query.update
        #
        # This test will always fail on specialized classes.
        try:
            super(TestSpecializedTree, self).test_rebuild()
        except Exception:
            import nose
            raise nose.SkipTest()
        else:
            raise AssertionError('Failure expected')  # pragma: no cover


Base2 = declarative_base()


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

    def test_rebuild(self):
        # See the following URL for caveats when using update on mapped
        # hierarchies:
        # http://docs.sqlalchemy.org/en/rel_0_9/orm/query.html?highlight=update#sqlalchemy.orm.query.Query.update
        #
        # This test will always fail on specialized classes.
        try:
            super(TestInheritanceTree, self).test_rebuild()
        except Exception:
            import nose
            raise nose.SkipTest()
        else:
            raise AssertionError('Failure expected')  # pragma: no cover
