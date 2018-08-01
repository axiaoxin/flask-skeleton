#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import pytest
import os

root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # noqa
sys.path.append(root_path)  # noqa
sys.path.append(os.path.join(root_path, 'app'))  # noqa


@pytest.fixture
def app():
    from app.apiserver import app
    config = app.config
    yield app
    app.config = config


@pytest.fixture
def client():
    from app.apiserver import app
    client = app.test_client()
    return client


@pytest.fixture
def utils():
    from app import utils
    return utils


@pytest.fixture
def mysql():
    from services import peewee_mysql
    yield peewee_mysql
    peewee_mysql.close()


@pytest.fixture
def redis():
    from services import redis
    yield redis
    redis.connection_pool.disconnect()
