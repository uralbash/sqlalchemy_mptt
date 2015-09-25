#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright (c) 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.
from .events import TreesManager
from .mixins import BaseNestedSets

__mixins__ = [BaseNestedSets]
__all__ = ['BaseNestedSets', 'mptt_sessionmaker']

tree_manager = TreesManager(BaseNestedSets)
tree_manager.register_events()
mptt_sessionmaker = tree_manager.register_factory
