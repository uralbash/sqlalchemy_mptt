[![Build Status](https://travis-ci.org/ITCase/sqlalchemy_mptt.svg?branch=master)](https://travis-ci.org/ITCase/sqlalchemy_mptt)
[![Coverage Status](https://coveralls.io/repos/ITCase/sqlalchemy_mptt/badge.png)](https://coveralls.io/r/ITCase/sqlalchemy_mptt)
[![Stories in Ready](https://badge.waffle.io/itcase/sqlalchemy_mptt.png?label=ready&title=Ready)](https://waffle.io/itcase/sqlalchemy_mptt)

Library for implementing Modified Preorder Tree Traversal with your SQLAlchemy Models and working with trees of Model instances, like django-mptt.

![Nested sets example](https://rawgithub.com/ITCase/sqlalchemy_mptt/master/docs/img/1_sqlalchemy_mptt_example.svg)

The nested set model is a particular technique for representing nested sets (also known as trees or hierarchies) in relational databases.

![Nested sets traversal](https://rawgithub.com/ITCase/sqlalchemy_mptt/master/docs/img/2_sqlalchemy_mptt_traversal.svg)

Installing
----------

Install from github:

    pip install git+http://github.com/ITCase/sqlalchemy_mptt.git
    
PyPi:

    pip install sqlalchemy_mptt

Source:

    python setup.py install

Usage
-----

Add mixin to model

```python
from sqlalchemy import Column, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy_mptt.mixins import BaseNestedSets

Base = declarative_base()


class Tree(Base, BaseNestedSets):
    __tablename__ = "tree"

    id = Column(Integer, primary_key=True)
    visible = Column(Boolean)

    def __repr__(self):
        return "<Node (%s)>" % self.id

Tree.register_tree()
```
Now you can add, move and delete obj
