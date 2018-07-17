#!/usr/bin/env python
# -*- coding: utf-8 -*-


def test_peewee_mysql_conn(app, mysql):
    cursor = mysql.execute_sql('select 1;')
    assert (1,) in cursor.fetchall()


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
        1/0

    rv = client.get('/400')
    assert 'invalid parameters' in rv.get_json()['msg']
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

    logger = init_logger('mylogger', 'debug', True,
                         'mylogger', '/tmp/pytest/', True)
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
    def normal():
        import time
        time.sleep(.1)

    @log_func_call
    def warning_too_long():
        import time
        time.sleep(app.config['CACHED_OVER_EXEC_MILLISECONDS'] / 1000.)

    normal()
    log = caplog.text.strip()
    assert "100" in log and log.endswith('ms')
    warning_too_long()
    log = caplog.text.strip()
    assert "WARNING" in log and log.endswith('ms')
