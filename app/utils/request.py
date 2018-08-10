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

    def __init__(self, key_prefix, limit, per, send_x_headers, scope):
        day_seconds = 60 * 60 * 24
        trunc = per if per < day_seconds else day_seconds
        offset = per if per < day_seconds else per + time.timezone
        self.reset = int(time.time()) // trunc * trunc + offset
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers
        self.scope = scope
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


def ratelimit(rate_exp=settings.DEFAULT_REQUEST_RATELIMIT_EXP,
              send_x_headers=True,
              on_over_limit=on_over_limit,
              scope_func=lambda: request.remote_addr,
              key_func=lambda: request.endpoint):
    '''
    :params rate_exp string/function string表达式或者返回string表达式的回调函数
        eg:"100/60" 或者 lambda: "100/60"，默认为"0/0"不限制
    :params send_x_headers bool 头信息中是否返回ratelimit信息，默认为True
    :params on_over_limit function 超过限制时的回调函数，默认返回JSON提示超过限制
    :params scope_func function 针对某个指标进行限制，默认为访问IP
    :params key_func function redis缓存次数用到的key的一部分值，默认为访问的endpoint

    usage:
    @ratelimit('100/60t l')
    def view():
       pass
    '''

    def decorator(f):
        def rate_limited(*args, **kwargs):
            rate = rate_exp if isinstance(rate_exp, basestring) else rate_exp()
            limit, per = map(int, rate.split('/'))
            # < 1 表示不限制
            if limit < 1 or per < 1:
                return f(*args, **kwargs)

            scope = scope_func()
            sign_key = 'ratelimit:sign:%s:%s:' % (key_func(), scope)
            rlimit = RateLimit(sign_key, limit, per, send_x_headers, scope)
            g._view_rate_limit = rlimit
            if on_over_limit is not None and rlimit.over_limit:
                return on_over_limit(rlimit)
            return f(*args, **kwargs)

        return update_wrapper(rate_limited, f)

    return decorator
