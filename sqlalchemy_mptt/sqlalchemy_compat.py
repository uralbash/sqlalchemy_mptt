# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright (c) 2025 Fayaz Yusuf Khan <fayaz.yusuf.khan@gmail.com>
# Distributed under terms of the MIT license.
"""Compatibility layer for SQLAlchemy versions."""
import sqlalchemy as sa


if sa.__version__ < '1.4':
    from sqlalchemy.ext.declarative import declarative_base
else:
    from sqlalchemy.orm import declarative_base


def select(*args, **kwargs):
    """Compatibility function for select."""
    if sa.__version__ < '1.4':
        return sa.select(args, **kwargs)
    else:
        return sa.select(*args, **kwargs)


def case(*args, **kwargs):
    """Compatibility function for case."""
    if sa.__version__ < '1.4':
        return sa.case(args, **kwargs)
    else:
        return sa.case(*args, **kwargs)


def get(session, model, id):
    """Compatibility function for getting an object by ID."""
    if sa.__version__ < '1.4':
        return session.query(model).get(id)
    else:
        return session.get(model, id)


__all__ = ["case", "declarative_base", "select"]
