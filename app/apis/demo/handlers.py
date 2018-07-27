#!/usr/bin/env python
# -*- coding: utf-8 -*-
from services import celery
from utils.log import app_logger
from . import notify_modules
import utils
import settings


def handle_message(data):
    method_name = data['notify_method'].lower()
    if method_name not in ['send_email', 'send_sms']:
        method_name = 'other_method'
    task = notify.apply_async(args=[data], queue=method_name)
    app_logger.debug(u'handle task:%r' % task.id)
    return task


@celery.task(
    bind=True,
    autoretry_for=[Exception],
    max_retries=10,
    default_retry_delay=60 * 1)
def notify(self, data):
    '''根据参数动态发送通知'''
    notify_module = notify_modules.import_module('tof')
    notify_method = getattr(notify_module, data['notify_method'])
    app_logger.debug(u'start call %s.%s' %
                     (notify_module.__name__, notify_method.__name__))
    if settings.FAKE_HANDLE_TASK:
        app_logger.info(u'fake handle message:%r' % data)
        result = utils.do_fake_task(result=(0, 'fake-result'))
    else:
        result = notify_method(data['send_to'], data['title'], data['content'])
    app_logger.debug(u'%r:notify complete:%r' % (self.request.id, result))
    return result


def get_notify_task(task_id):
    '''获取异步任务'''
    return notify.AsyncResult(task_id)
