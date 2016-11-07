#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import datetime
import types
import inspect
import re

from utils.log import app_logger


def is_ipv4(ip):
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
        return True
    return False


def datetime2timestamp(dt, is_int=True):
    ts = time.mktime(dt.timetuple())
    if is_int:
        ts = int(ts)
    return ts


def timestamp2str(ts, str_format='%Y-%m-%d %H:%M:%S'):
    dt = datetime.datetime.utcfromtimestamp(ts)
    return dt.strftime(str_format)


def datetime2str(dt, str_format='%Y-%m-%d %H:%M:%S'):
    return dt.strftime(str_format)


def register_decorators_on_module_funcs(modules, decorators):
    '''将decorator自动注册到module中的所有函数
    函数中设置__nodeco__属性为False或者以下划线开头的名称
    则不自动注册任何装饰器
    eg:
        def func():
            pass
        func.__nodeco__ = True
    '''
    if not isinstance(modules, (list, tuple)):
        modules = [modules]
    if not isinstance(decorators, (list, tuple)):
        decorators = [decorators]
    for m in modules:
        for funcname, func in vars(m).iteritems():
            if (isinstance(func, types.FunctionType) and
                    not funcname.startswith('_') and
                    func.__module__ == m.__name__):
                if getattr(func, '__nodeco__', False):
                    continue
                for deco in decorators:
                    app_logger.debug('register %s on %s.%s' %
                                     (deco.__name__, m.__name__, funcname))
                    func = deco(func)
                    vars(m)[funcname] = func


def get_func_name(func, full=True):
    if full:
        return '{}.{}'.format(inspect.getmodule(func).__name__, func.__name__)
    else:
        return func.__name__


def to_curl(request):
    headers = ["'{0}: {1}'".format(k, v) for k, v in request.headers.items()]
    headers = " -H ".join(sorted(headers))

    command = "curl -X {method} -H {headers} -d '{data}' '{uri}'".format(
        data=request.body or "",
        headers=headers,
        method=request.method,
        uri=request.url, )
    return command


def do_fake_task(sec=0.05, result='the-fake-result'):
    import time
    time.sleep(sec)
    return result
