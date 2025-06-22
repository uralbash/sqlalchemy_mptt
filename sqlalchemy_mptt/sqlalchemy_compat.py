# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright (c) 2025 Fayaz Yusuf Khan <fayaz.yusuf.khan@gmail.com>
# Distributed under terms of the MIT license.
"""Compatibility layer for SQLAlchemy versions."""
import sqlalchemy as sa


class LegacySQLAlchemyAPI:
    """A class to provide compatibility for legacy SQLAlchemy versions (1.0 - 1.3)."""

    @staticmethod
    def declarative_base(*args, **kwargs):
        from sqlalchemy.ext.declarative import declarative_base
        return declarative_base(*args, **kwargs)

    @staticmethod
    def select(*args, **kwargs):
        return sa.select(args, **kwargs)

    @staticmethod
    def case(*args, **kwargs):
        return sa.case(args, **kwargs)

    @staticmethod
    def get(session, model, id):
        return session.query(model).get(id)


class ModernSQLAlchemyAPI:
    """A class to provide compatibility for modern SQLAlchemy versions (1.4+)."""

    @staticmethod
    def declarative_base(*args, **kwargs):
        from sqlalchemy.orm import declarative_base
        return declarative_base(*args, **kwargs)

    @staticmethod
    def select(*args, **kwargs):
        return sa.select(*args, **kwargs)

    @staticmethod
    def case(*args, **kwargs):
        return sa.case(*args, **kwargs)

    @staticmethod
    def get(session, model, id):
        return session.get(model, id)


if sa.__version__ < '1.4':
    compat_layer = LegacySQLAlchemyAPI()
else:
    compat_layer = ModernSQLAlchemyAPI()
