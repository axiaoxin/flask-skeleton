#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import time
import datetime
import types
import inspect
import re
import socket

from flask import abort
from cerberus import Validator
# http://docs.python-cerberus.org/en/stable/validation-rules.html

from utils.log import app_logger
import settings


def hostname():
    try:
        return socket.gethostname()
    except Exception as e:
        app_logger.exception(e)


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


validator = Validator()


def validate_dict(data, schema, allow_unknown=True):
    validator.allow_unkown = allow_unknown
    if not validator.validate(data, schema):
        return abort(400, validator.errors)
    return True


def pagination(items_count, page_num, page_size):
    if page_num > 0 and page_size > 0:
        pages_count = int(math.ceil(items_count / float(page_size)))
        has_next = True if page_num + 1 <= pages_count else False
        has_prev = True if page_num - 1 > 0 else False
        next_page_num = page_num + 1 if has_next else page_num
        prev_page_num = page_num - 1 if has_prev else page_num
        return {
            'items_count': items_count,
            'pages_count': pages_count,
            'page_num': page_num,
            'page_size': page_size,
            'has_next': has_next,
            'has_prev': has_prev,
            'next_page_num': next_page_num,
            'prev_page_num': prev_page_num,
        }


def send_flask_mail(send_to,
                    title,
                    content,
                    html=True,
                    sender=settings.MAIL_DEFAULT_SENDER,
                    cc=None,
                    attachments=None):
    '''使用邮件服务器发送邮件
    :params send_to list: 收件人列表
    :params title string: 邮件标题
    :params content string: 邮件内容
    :params html bool: 邮件内容是否为HTML格式，默认为True
    :params sender string: 发件人
    :params cc list: cc列表
    :params attachments dict: 附件
    eg: {"filename": "x.png", "content_type": "image/png", "data": img.read()}
    '''
    from services import mail, app
    from flask_mail import Message

    with app.app_context():
        msg = Message()
        msg.recipients = send_to
        msg.cc = cc
        msg.subject = title
        msg.sender = sender
        if html:
            msg.html = content
        else:
            msg.body = content
        if attachments:
            msg.attach(**attachments)
        mail.send(msg)
