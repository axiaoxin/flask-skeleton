#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import uuid
from functools import update_wrapper

from flask import request, g
from celery import signals

from services import redis
from response import response, RetCode
from utils.log import app_logger
import settings


def g_get(ctxkey):
    from flask import _app_ctx_stack, g
    if _app_ctx_stack.top is not None:
        return g.get(ctxkey, None)


def celery_task_request_get(key):
    from celery import current_task
    if current_task._get_current_object() is not None:
        return current_task.request.get(key, None)

##############
# REQUEST ID #
##############


def x_request_id():
    request_id = request.headers.get(settings.REQUEST_ID_KEY, '').strip()
    if not request_id:
        request_id = str(uuid.uuid4())
    return request_id


def current_request_id():
    """
    Get request id from flask's G object
    :return: The id or None if not found.
    """
    request_id = g_get('request_id')
    if not request_id:
        request_id = celery_task_request_get('request_id')
    return request_id


def celery_persist_request_id(headers, **kwargs):
    request_id = current_request_id()
    headers['request_id'] = request_id
    app_logger.debug('Forwarding request_id %r to worker.' % request_id)
# Forward request_id to celery tasks
signals.before_task_publish.connect(celery_persist_request_id)

##############
# RATE LIMIT #
##############


class RateLimit(object):
    expiration_window = 2

    def __init__(self, key_prefix, limit, per, send_x_headers):
        self.reset = (int(time.time()) // per) * per + per
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers
        p = redis.pipeline()
        p.incr(self.key)
        p.expireat(self.key, self.reset + self.expiration_window)
        self.current = p.execute()[0]

    remaining = property(lambda x: max(x.limit - x.current, 0))
    over_limit = property(lambda x: x.current > x.limit)


def get_view_rate_limit():
    return getattr(g, '_view_rate_limit', None)


def on_over_limit(limit):
    return response(code=RetCode.RATE_LIMIT_ERROR)


def ratelimit(counts=settings.DEFAULT_REQUEST_RATELIMIT_COUNTS,
              seconds=settings.DEFAULT_REQUEST_RATELIMIT_SECONDS,
              send_x_headers=True,
              on_over_limit=on_over_limit,
              scope_func=lambda: request.remote_addr,
              key_func=lambda: request.endpoint):
    '''usage:
    @ratelimit(counts=100, seconds=60)
    def view():
       pass
    '''

    def decorator(f):
        def rate_limited(*args, **kwargs):
            limit = counts if isinstance(counts, (int, float)) else counts()
            per = seconds if isinstance(seconds, (int, float)) else seconds()
            # < 1 表示不限制
            if limit < 1 or per < 1:
                return f(*args, **kwargs)

            sign_key = 'ratelimit:sign:%s:%s:' % (key_func(), scope_func())
            rlimit = RateLimit(sign_key, limit, per, send_x_headers)
            g._view_rate_limit = rlimit
            if on_over_limit is not None and rlimit.over_limit:
                return on_over_limit(rlimit)
            return f(*args, **kwargs)

        return update_wrapper(rate_limited, f)

    return decorator
