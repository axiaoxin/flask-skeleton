# coding:utf-8
import cPickle
import time
import urlparse
from functools import wraps

from flask import request
from redis.exceptions import ConnectionError

import settings
from utils import get_func_name
from utils.log import app_logger
from services import redis


def cached_call(over_ms=None,
                expire=settings.CACHED_EXPIRE_SECONDS,
                tag='',
                namespace='views'):
    prefix = 'cached_call'

    def cached_deco(func):
        @wraps(func)
        def wrapper(*func_args, **func_kwargs):
            if not settings.CACHED_CALL:
                return func(*func_args, **func_kwargs)
            try:
                redis.info()
            except ConnectionError:
                app_logger.warning(
                    "redis connection fail, can't use the cache")
                return func(*func_args, **func_kwargs)

            if namespace == 'views':
                if request.method == 'GET':
                    url = urlparse.urlsplit(request.url)
                    key = ':'.join(field
                                   for field in [prefix, namespace, tag,
                                                 url.path, url.query] if field)
                else:
                    return func(*func_args, **func_kwargs)
            elif namespace == 'funcs':
                params = '%s&%s' % (str(func_args), str(func_kwargs))
                funcname = get_func_name(func)
                key = ':'.join(
                    field
                    for field in [prefix, namespace, tag, funcname, params]
                    if field)

            data = redis.get(key)
            if data is None:
                start_time = time.time()
                result = func(*func_args, **func_kwargs)
                exec_time = (time.time() - start_time) * 1000
                if over_ms is None:
                    if exec_time > settings.CACHED_OVER_EXEC_MILLISECONDS:
                        redis.setex(key, cPickle.dumps(result), expire)
                        app_logger.debug(u'cached:%r' % key)
                else:
                    if exec_time > over_ms:
                        redis.setex(key, cPickle.dumps(result), expire)
                        app_logger.debug(u'cached:%r' % key)
                return result
            return cPickle.loads(data)

        return wrapper

    return cached_deco


def get_redislock(name,
                  timeout=settings.REDIS_LOCK_TIMEOUT,
                  blocking_timeout=None):
    ''' Useage:

    lock = get_redislock('print_arg:%s' % arg, blocking_timeout=1)
    if lock.acquire():
        try:
            do_something
        finally:
            lock.release()
    else:
        logger.warning('blocking')

    '''
    key = 'lock:' + name
    lock = redis.lock(
        name=key, timeout=timeout, blocking_timeout=blocking_timeout)
    return lock
