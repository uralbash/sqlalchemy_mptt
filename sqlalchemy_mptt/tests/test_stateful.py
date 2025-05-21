from hypothesis import assume, given, settings, strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, invariant, rule
from sqlalchemy import Column, Integer, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_mptt import BaseNestedSets, mptt_sessionmaker


Base = declarative_base()


class Tree(Base, BaseNestedSets):
    __tablename__ = "tree"

    id = Column(Integer, primary_key=True)
    visible = Column(Boolean)

    def __repr__(self):
        return "<Node (%s)>" % self.id


class TreeStateMachine(RuleBasedStateMachine):

    def __init__(self):
        super().__init__()
        self.engine = create_engine("sqlite:///:memory:")
        Session = mptt_sessionmaker(sessionmaker(bind=self.engine))
        self.session = Session()
        Base.metadata.create_all(self.engine)

    node = Bundle('node')

    @rule(target=node, visible=st.none() | st.booleans())
    def add_root_node(self, visible):
        node = Tree(visible=visible)
        self.session.add(node)
        self.session.flush()
        assert node.left < node.right
        return node

    @rule(target=node, node=node, visible=st.none() | st.booleans())
    def add_child(self, node, visible):
        assume(node in self.session)
        child = Tree(parent=node, visible=visible)
        self.session.add(child)
        self.session.flush()
        assert node.left < child.left < child.right < node.right
        return child

    @rule(node=node)
    def delete_child(self, node):
        assume(node in self.session)
        self.session.delete(node)
        self.session.flush()

    @invariant()
    def check_get_tree_integrity(self):
        response = Tree.get_tree(self.session)
        assert isinstance(response, list)
        for node in response:
            self.session.refresh(node['node'])
            validate_get_tree_node(node)

    @invariant()
    @given(st.none() | st.booleans())
    def check_get_tree_with_custom_query(self, visible):
        response = Tree.get_tree(self.session, query=lambda x: x.filter_by(visible=visible))
        assert isinstance(response, list)
        for node in response:
            self.session.refresh(node['node'])
            validate_get_tree_node_for_custom_query(node)


def validate_get_tree_node(node_response, level=1):
    node = node_response['node']
    assert node.level == level
    if len(node.children):
        assert 'children' in node_response.keys()
        children_response = node_response['children']
        assert len(node.children) == len(children_response)
        for child, child_response in zip(node.children, children_response):
            assert child == child_response['node']
            validate_get_tree_node(child_response, level=level + 1)


def validate_get_tree_node_for_custom_query(node_response):
    node = node_response['node']
    if 'children' in node_response.keys():
        for child_response in node_response['children']:
            assert child_response['node'].parent == node
            validate_get_tree_node_for_custom_query(child_response)


TestTreeStates = TreeStateMachine.TestCase
TestTreeStates.settings = settings(
    max_examples=50, stateful_step_count=100
)
