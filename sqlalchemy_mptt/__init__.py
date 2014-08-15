#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

from sqlalchemy.orm import mapper
from .mixins import BaseNestedSets
from .events import TreesManager

__version__ = "0.0.8"
__mixins__ = [BaseNestedSets]
__all__ = ['BaseNestedSets', 'mptt_sessionmaker']

tree_manager = TreesManager(BaseNestedSets)
tree_manager.register_mapper(mapper)
mptt_sessionmaker = tree_manager.register_factory
