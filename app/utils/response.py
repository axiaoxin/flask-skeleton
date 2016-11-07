#!/usr/bin/env python
# *- coding: utf-8 -*-
import ujson as json

from flask import Response
import settings
import stringcase
from utils.log import app_logger


class RetCode(object):
    SUCCESS = 0
    FAILURE = -1
    PARAMS_ERROR = 400
    ENTRY_NOT_FOUND = 404
    RATE_LIMIT_ERROR = 429
    SERVER_ERROR = 500


RetCodeMsg = {
    RetCode.SUCCESS: u'SUCCUSS',
    RetCode.FAILURE: u'FAILURE',
    RetCode.PARAMS_ERROR: u'PARAMS ERROR',
    RetCode.ENTRY_NOT_FOUND: u'ENTRY NOT FOUND',
    RetCode.RATE_LIMIT_ERROR: u'HIT THE RATE LIMIT',
    RetCode.SERVER_ERROR: u'INTERNAL SERVER ERROR',
}


def keycase_convert(obj, func):
    if isinstance(obj, dict):
        return {func(k): keycase_convert(v, func) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [keycase_convert(elem, func) for elem in obj]
    else:
        return obj


def get_support_keycase():
    return [i for i in dir(stringcase) if i.endswith('case')]


def jsonify_(data):
    keycase = settings.JSON_KEYCASE
    if keycase:
        try:
            casefunc = getattr(stringcase, keycase)
            data = keycase_convert(data, casefunc)
        except AttributeError:
            app_logger.warning(
                u'%s keycase is not supported, response default json. '
                u'Supported keycase: %s' % (keycase, get_support_keycase()))
    js = json.dumps(data, ensure_ascii=settings.JSON_AS_ASCII)
    return Response(js, mimetype='application/json')


def response(data=None, code=RetCode.SUCCESS, msg=None):
    result = {'code': code, 'data': data}
    if msg:
        result['msg'] = msg
    else:
        result['msg'] = RetCodeMsg.get(code, '')

    return jsonify_(result), code if code > 100 else 200
