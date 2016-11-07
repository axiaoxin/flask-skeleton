#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from contextlib import contextmanager

import peewee
from flask import abort
from peewee import Model

import utils
from services import peewee_mysql
from utils.log import app_logger


class MySQLBaseModel(Model):
    class Meta:
        database = peewee_mysql


@contextmanager
def sa_session_scope(session, commit=False):
    """Provide a transactional scope around a series of operations
    for sqlalchemy."""
    try:
        yield session
        if commit:
            session.commit()
    except Exception as e:
        session.rollback()
        app_logger.error(e)
        raise
    finally:
        session.close()


def model2dict(model, pop=[], orm='peewee'):
    if not model:
        return

    data = model.__dict__
    if orm == 'sqlalchemy':
        data.pop('_sa_instance_state', None)
    elif orm == 'peewee':
        if peewee.__version__.startswith('3'):
            data = model.__data__
        elif peewee.__version__.startswith('2'):
            data = model._data

    for k, v in data.iteritems():
        if isinstance(v, datetime.date):
            data[k] = utils.datetime2str(v, '%Y-%m-%d')
        if isinstance(v, datetime.datetime):
            data[k] = utils.datetime2str(v)

    for field in pop:
        data.pop(field, None)

    return data


def get_object_or_404(model, *expressions):
    try:
        return model.get(*expressions)
    except model.DoesNotExist:
        abort(404)
