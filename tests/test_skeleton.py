#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cPickle
import time


def test_peewee_mysql_conn(app, mysql):
    cursor = mysql.execute_sql('select 1;')
    assert (1, ) in cursor.fetchall()


def test_redis_conn(app, redis):
    #  print 'redis cluster:', app.config['REDIS_CLUSTER']
    #  print 'redis sentinel:', app.config['REDIS_SENTINEL']
    #  print 'redis url:', app.config['REDIS_URL']
    assert '1' in redis.echo('1')


def test_json_keycase(utils):
    from utils import response
    resp_obj = response.jsonify_({'the_key': 'value'}, 'camelcase')
    assert 'theKey' in resp_obj.get_json()
    resp_obj = response.jsonify_({'theKey': 'value'}, 'snakecase')
    assert 'the_key' in resp_obj.get_json()
    resp_obj = response.jsonify_({'the_key': 'value'}, 'dotcase')
    assert 'the.key' in resp_obj.get_json()


def test_error_handler(app, client, utils):

    from utils import response
    from flask import request

    @app.route('/400')
    def tmp():
        request.values['key']

    @app.route('/500')
    def tmp500():
        1 / 0

    rv = client.get('/400')
    assert rv.status_code == 400

    rv = client.get('/404')
    assert response.RetCodeMsg.get(404) in rv.get_json()['msg']
    assert rv.status_code == 404

    app.config['DEBUG'] = False
    rv = client.get('/500')
    assert 'sentry_event_id' in rv.get_json()['data']
    assert rv.status_code == 500


def notest_split_logfile_by_level(app, client):
    from utils.log import init_logger

    logger = init_logger('mylogger', 'debug', True, 'mylogger', '/tmp/pytest/',
                         True)
    logger.debug('msg')
    logfile = open('/tmp/pytest/mylogger.debug.log')
    log = logfile.readlines()[-1]
    assert '[DEBUG]' in log
    logfile.close()

    logger.info('msg')
    logfile = open('/tmp/pytest/mylogger.info.log')
    log = logfile.readlines()[-1]
    assert '[INFO]' in log
    logfile.close()
    logfile = open('/tmp/pytest/mylogger.debug.log')
    log = logfile.readlines()[-1]
    assert '[INFO]' not in log
    logfile.close()

    logger.warning('msg')
    logfile = open('/tmp/pytest/mylogger.warning.log')
    log = logfile.readlines()[-1]
    assert '[WARNING]' in log
    logfile.close()
    logfile = open('/tmp/pytest/mylogger.info.log')
    log = logfile.readlines()[-1]
    assert '[WARNING]' not in log
    logfile = open('/tmp/pytest/mylogger.debug.log')
    log = logfile.readlines()[-1]
    assert '[WARNING]' not in log
    logfile.close()

    import os
    os.system('rm -rf /tmp/pytest')


def test_log_func_call(utils, app, caplog):
    from utils.log import log_func_call

    @log_func_call
    def func():
        pass

    func()
    log = caplog.text.strip()
    assert log.endswith('ms')


def test_cached_call_funcs(app, utils, redis, caplog):
    from utils.cache import cached_call
    from utils.cache import _generate_key
    from utils import get_func_name

    # run fast, dont need to cache
    @cached_call(
        cached_over_ms=app.config['CACHED_OVER_EXEC_MILLISECONDS'],
        expire=app.config['CACHED_EXPIRE_SECONDS'],
        tag='',
        namespace='funcs')
    def no_cache():
        time.sleep(0)
        return "no_cache"

    rv = no_cache()
    funcname = get_func_name(no_cache)
    params = '()&{}'
    key = _generate_key('funcs', '', funcname=funcname, params=params)
    print 'key:', key

    data = redis.get(key)
    assert data is None

    # over time need to cache
    @cached_call(
        cached_over_ms=app.config['CACHED_OVER_EXEC_MILLISECONDS'],
        expire=app.config['CACHED_EXPIRE_SECONDS'],
        tag='',
        namespace='funcs')
    def cache_it():
        time.sleep(app.config['CACHED_OVER_EXEC_MILLISECONDS'] / 1000. + 1)
        return "cache_it"

    rv = cache_it()
    funcname = get_func_name(cache_it)
    params = '()&{}'
    key = _generate_key('funcs', '', funcname=funcname, params=params)
    print 'key:', key

    data = redis.get(key)
    assert data is not None
    cached_rv = cPickle.loads(data)
    print 'func rv:', rv, 'cached rv:', cached_rv
    assert rv == cached_rv
    cache_it()
    log = caplog.text.strip()
    assert 'data from cache' in log
    redis.delete(key)

    # cache with func params
    @cached_call(
        cached_over_ms=app.config['CACHED_OVER_EXEC_MILLISECONDS'],
        expire=app.config['CACHED_EXPIRE_SECONDS'],
        tag='',
        namespace='funcs')
    def cache_with_params(x, y, z):
        time.sleep(app.config['CACHED_OVER_EXEC_MILLISECONDS'] / 1000. + 1)
        return u"cache_with_params %s + %s = %s %s" % (x, y, x + y, z)

    rv = cache_with_params(1, 2, z='zzz')

    funcname = get_func_name(cache_with_params)
    params = "(1, 2)&{'z': 'zzz'}"
    key = _generate_key('funcs', '', funcname=funcname, params=params)
    print 'key:', key

    data = redis.get(key)
    assert data is not None
    cached_rv = cPickle.loads(data)
    print 'func rv:', rv, 'cached rv:', cached_rv
    assert rv == cached_rv
    cache_with_params(1, 2, z='zzz')
    log = caplog.text.strip()
    assert 'data from cache' in log
    redis.delete(key)


def test_cached_call_views(app, client, redis, caplog):
    from utils.cache import cached_call
    from utils.cache import _generate_key
    from flask import request

    @app.route('/no_cacheview', methods=['GET', 'POST'])
    @cached_call(
        cached_over_ms=app.config['CACHED_OVER_EXEC_MILLISECONDS'],
        expire=app.config['CACHED_EXPIRE_SECONDS'],
        tag='',
        namespace='views')
    def no_cacheview():
        time.sleep(0)
        return request.method

    @app.route('/cacheview', methods=['GET', 'POST'])
    @cached_call(
        cached_over_ms=app.config['CACHED_OVER_EXEC_MILLISECONDS'],
        expire=app.config['CACHED_EXPIRE_SECONDS'],
        tag='',
        namespace='views')
    def cacheview():
        time.sleep(app.config['CACHED_OVER_EXEC_MILLISECONDS'] / 1000. + 1)
        return request.method

    @app.route('/cacheviewparams', methods=['GET'])
    @cached_call(
        cached_over_ms=app.config['CACHED_OVER_EXEC_MILLISECONDS'],
        expire=app.config['CACHED_EXPIRE_SECONDS'],
        tag='',
        namespace='views')
    def cacheviewparams():
        time.sleep(app.config['CACHED_OVER_EXEC_MILLISECONDS'] / 1000. + 1)
        return request.values.get('x') + request.values.get('y')

    # run fast, dont need to cache
    # dont cache post method
    url_path = '/no_cacheview'
    url_query = None
    key = _generate_key('views', '', url_path=url_path, url_query=url_query)
    print 'key:', key

    client.get(url_path)
    data = redis.get(key)
    assert data is None

    client.post(url_path)
    data = redis.get(key)
    assert data is None

    # over time cache it
    # dont cache post method
    url_path = '/cacheview'
    url_query = None
    key = _generate_key('views', '', url_path=url_path, url_query=url_query)
    print 'key:', key

    rv = client.post(url_path).data
    data = redis.get(key)
    assert data is None

    rv = client.get(url_path).data
    data = redis.get(key)
    assert data is not None
    cached_rv = cPickle.loads(data)
    print 'func rv:', rv, 'cached rv:', cached_rv
    assert rv == cached_rv
    client.get(url_path)
    log = caplog.text.strip()
    assert 'data from cache' in log
    redis.delete(key)

    # cache with param
    url_path = '/cacheviewparams'
    url_query = "x=Hello&y=World"
    key = _generate_key('views', '', url_path=url_path, url_query=url_query)
    print 'key:', key

    rv = client.get(url_path + '?' + url_query).data
    data = redis.get(key)
    assert data is not None
    cached_rv = cPickle.loads(data)
    print 'func rv:', rv, 'cached rv:', cached_rv
    assert rv == cached_rv
    client.get(url_path + '?' + url_query)
    log = caplog.text.strip()
    assert 'data from cache' in log
    redis.delete(key)


s = ''


def test_redis_lock(app, utils, redis):
    from utils.cache import get_redislock

    global s

    def nolock(sleep):
        global s
        s += 'sleep:'
        time.sleep(sleep)
        s += 'wakeup'

    def blocklock(sleep):
        global s
        lock = get_redislock(
            name='test-the-lock',
            timeout=app.config['REDIS_LOCK_TIMEOUT'],
            blocking_timeout=0.5)
        if lock.acquire():
            try:
                s += 'sleep:'
                time.sleep(sleep)
                s += 'wakeup'
            finally:
                lock.release()
        elif lock.blocking_timeout is not None:
            s += 'block timeout'

    def noblocklock(sleep):
        global s
        lock = get_redislock(
            name='test-the-lock',
            timeout=app.config['REDIS_LOCK_TIMEOUT'],
            blocking_timeout=None)
        if lock.acquire():
            try:
                s += 'sleep:'
                time.sleep(sleep)
                s += 'wakeup'
            finally:
                lock.release()
        elif lock.blocking_timeout is not None:
            s += 'block timeout'

    import gevent
    from gevent import monkey
    monkey.patch_all()
    gevent.joinall([
        gevent.spawn(nolock, 1),
        gevent.spawn(nolock, 1),
    ])
    print s
    assert s == 'sleep:sleep:wakeupwakeup'

    s = ''
    gevent.joinall([
        gevent.spawn(blocklock, 1),
        gevent.spawn(blocklock, 1),
    ])
    print s
    assert s == 'sleep:block timeoutwakeup'

    s = ''
    gevent.joinall([
        gevent.spawn(noblocklock, 1),
        gevent.spawn(noblocklock, 1),
    ])
    print s
    assert s == 'sleep:wakeupsleep:wakeup'
