# !/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
reload(sys)  # noqa
sys.setdefaultencoding('utf8')  # noqa

from flask import g, redirect, url_for

from apis.docs import docs
from apis.demo.routes import message_api
from services import app, sentry
from utils.response import RetCode, response
from utils import request
import settings


@app.errorhandler(400)
def bad_request(error):
    return response(code=RetCode.PARAMS_ERROR, msg=error.description)


@app.errorhandler(404)
def api_not_found(error):
    return response(code=RetCode.ENTITY_NOT_FOUND)


@app.errorhandler(500)
def server_error(error):
    data = {
        'sentry_event_id': g.sentry_event_id,
        'public_dsn': sentry.client.get_public_dsn('http'),
        'error': str(error)
    }
    return response(data, RetCode.SERVER_ERROR)


@app.before_request
def persist_request_id():
    g.request_id = request.x_request_id()


@app.after_request
def inject_x_request_id_headers(response):
    response.headers.add(settings.REQUEST_ID_KEY,
                         request.current_request_id())
    return response


@app.after_request
def inject_x_rate_headers(response):
    limit = request.get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Current', str(limit.current))
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
        h.add('X-RateLimit-Per', str(limit.per))
    return response


@app.route('/')
def hello_world():
    return response(data='Hello!')


@app.route('/favicon.ico')
def ico():
    return redirect(url_for('static', filename='img/favicon.ico'))


app.register_blueprint(docs, url_prefix='/docs')
app.register_blueprint(message_api, url_prefix='/demo')

if __name__ == '__main__':
    app.run()
