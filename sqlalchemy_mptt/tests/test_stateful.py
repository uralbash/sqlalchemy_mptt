# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2025 fayazkhan <fayaz.yusuf.khan@gmail.com>
#
# Distributed under terms of the MIT license.
"""Test cases written using Hypothesis stateful testing framework."""
from hypothesis import HealthCheck, settings, strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, consumes, invariant, rule
from sqlalchemy import Column, Integer, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import joinedload, sessionmaker

from sqlalchemy_mptt import BaseNestedSets, mptt_sessionmaker


Base = declarative_base()


class Tree(Base, BaseNestedSets):
    __tablename__ = "tree"

    id = Column(Integer, primary_key=True)
    visible = Column(Boolean)

    def __repr__(self):
        return "<Node (%s)>" % self.id


class TreeStateMachine(RuleBasedStateMachine):
    """A state machine with various possible actions and transitions for the Tree model."""

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
        self.session.commit()
        assert node.left < node.right
        return node

    @rule(node=consumes(node))
    def delete_node(self, node):
        # Consume all descendants of the node
        for name, value in list(self.names_to_values.items()):
            if value not in self.session or node.is_ancestor_of(value):
                for var_reference in self.bundles["node"][:]:
                    if var_reference.name == name:
                        self.bundles["node"].remove(var_reference)
                # Remove the object as well for garbage collection
                del self.names_to_values[name]
        self.session.delete(node)
        self.session.commit()

    @rule(target=node, node=node, visible=st.none() | st.booleans())
    def add_child(self, node, visible):
        child = Tree(parent=node, visible=visible)
        self.session.add(child)
        self.session.commit()
        assert node.left < child.left < child.right < node.right
        return child

    @invariant()
    def check_get_tree_integrity(self):
        """Check that get_tree response is valid after each operation."""
        response = Tree.get_tree(
            self.session,
            query=lambda x: x.execution_options(populate_existing=True).options(joinedload(Tree.children)))
        assert isinstance(response, list)
        for node in response:
            validate_get_tree_node(node)

    @invariant()
    def check_get_tree_with_custom_query(self):
        """Check that get_tree response is valid with custom queries."""
        for visible in [None, True, False]:
            response = Tree.get_tree(
                self.session,
                query=lambda x: x.filter_by(visible=visible)
                    .execution_options(populate_existing=True).options(joinedload(Tree.children)))
            assert isinstance(response, list)
            for node in response:
                validate_get_tree_node_for_custom_query(node)


def validate_get_tree_node(node_response, level=1):
    """Validate the structure of a node response from get_tree."""
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
    """Validate the structure of a node response from get_tree with custom query."""
    node = node_response['node']
    if 'children' in node_response.keys():
        for child_response in node_response['children']:
            assert child_response['node'].parent == node
            validate_get_tree_node_for_custom_query(child_response)


# Export the stateful test case
TestTreeStates = TreeStateMachine.TestCase
TestTreeStates.settings = settings(
    max_examples=75, stateful_step_count=25#, suppress_health_check=[HealthCheck.too_slow]
)
