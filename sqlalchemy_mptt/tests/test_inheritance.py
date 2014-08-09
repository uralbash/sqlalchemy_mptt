import unittest

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..mixins import BaseNestedSets

Base = declarative_base()


class GenericTree(Base, BaseNestedSets):
    __tablename__ = "generic"

    id = sa.Column(sa.Integer, primary_key=True)
    type = sa.Column(sa.Integer, default=0)

    __mapper_args__ = {
        'polymorphic_identity': 0,
        'polymorphic_on': type,
    }

    def __repr__(self):
        return "<Node (%s)>" % self.id

    @classmethod
    def __declare_last__(cls):
        cls.register_tree()


class SpecializedTree(GenericTree):
    __tablename__ = "specialized"

    id = sa.Column(sa.Integer, sa.ForeignKey(GenericTree.id), primary_key=True)

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
        self.session.add(GenericTree(id=1))
        self.session.commit()

        tree = self.session.query(GenericTree).get(1)
        self.assertEqual(tree.id, 1)
        self.assertEqual(tree.tree_id, 1)

    def test_create_spec(self):
        self.session.add(SpecializedTree(id=1))
        self.session.commit()

        tree = self.session.query(SpecializedTree).get(1)
        self.assertEqual(tree.id, 1)
        self.assertEqual(tree.tree_id, 1)

    def test_create_delete(self):
        parent = SpecializedTree(id=1)

        child1 = SpecializedTree(id=2, parent=parent)
        child2 = GenericTree(id=3, parent=parent)

        GenericTree(id=4, parent=child2)
        SpecializedTree(id=5, parent=child2)

        self.session.add(parent)
        self.session.commit()

        tree = self.session.query(SpecializedTree).get(1)
        self.assertEqual(tree.id, 1)
        self.assertEqual(tree.tree_id, 1)

        self.session.delete(child1)
        self.session.commit()

        self.assertEquals(None, self.session.query(SpecializedTree).get(2))

        self.session.delete(child2)
        self.session.commit()

        self.assertEquals(None, self.session.query(SpecializedTree).get(3))
        self.assertEquals(None, self.session.query(SpecializedTree).get(4))
        self.assertEquals(None, self.session.query(SpecializedTree).get(5))
