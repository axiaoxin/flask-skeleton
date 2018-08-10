#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import time

from celery import Celery
from flask import Flask
from raven import Client
from raven.contrib.flask import Sentry
from raven.contrib.celery import register_signal, register_logger_signal
from werkzeug.contrib.fixers import ProxyFix
from requests import Session
from requests.adapters import HTTPAdapter
from flasgger import Swagger
from flask_flatpages import FlatPages
from playhouse.pool import PooledMySQLDatabase

import settings

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config.from_object(settings)


class PooledAutoReconnectionMySQLDatabase(PooledMySQLDatabase):
    def _connect(self):
        retries = 4
        sleep = 0
        for i in range(retries):
            try:
                return super(PooledAutoReconnectionMySQLDatabase,
                             self)._connect()
            except Exception as e:
                # if connect error, retry 3 times
                from utils.log import app_logger
                app_logger.warning('%s. Connect times: %d' % (str(e), i))
            time.sleep(sleep)
        raise e


peewee_mysql = PooledAutoReconnectionMySQLDatabase(
    database=settings.MYSQL_DBNAME,
    user=settings.MYSQL_USER,
    password=settings.MYSQL_PASSWORD,
    host=settings.MYSQL_HOST,
    port=settings.MYSQL_PORT,
    max_connections=settings.DB_POOL_MAX_CONNECTIONS,
    stale_timeout=settings.DB_POOL_STALE_TIMEOUT,
    timeout=settings.DB_POOL_WAIT_TIMEOUT)

sentry_client = Client(settings.SENTRY_DSN)
sentry = Sentry(app, client=sentry_client)
register_logger_signal(sentry_client)
register_logger_signal(sentry_client, loglevel=logging.INFO)
register_signal(sentry_client)
register_signal(sentry_client, ignore_expected=True)

celery = Celery(
    app.name,
    broker=settings.BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND)
celery.conf.update(app.config)

requests = Session()
adapter = HTTPAdapter(
    pool_connections=settings.REQUESTS_POOL_SIZE,
    pool_maxsize=settings.REQUESTS_POOL_SIZE)
requests.mount('http://', adapter)
requests.mount('https://', adapter)
requests.headers['X-Caller'] = settings.SERVICE_NAME

swagger = Swagger(app)

flatpages = FlatPages(app)


def get_redis_client():
    if settings.REDIS_CLUSTER:
        from rediscluster import StrictRedisCluster
        redis = StrictRedisCluster(
            startup_nodes=settings.REDIS_CLUSTER['nodes'],
            decode_responses=True,
            password=settings.REDIS_CLUSTER['password'])
    elif settings.REDIS_SENTINEL:
        from redis.sentinel import Sentinel
        sentinel = Sentinel(
            settings.REDIS_SENTINEL['nodes'],
            socket_timeout=settings.REDIS_SENTINEL.get('socket_timeout', 0.1))
        redis = sentinel.master_for(
            settings.REDIS_SENTINEL['master_name'],
            db=settings.REDIS_SENTINEL['db'],
            password=settings.REDIS_SENTINEL['password'])
    else:
        from redis import Redis
        redis = Redis.from_url(settings.REDIS_URL)
    return redis


redis = get_redis_client()
