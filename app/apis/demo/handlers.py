#!/usr/bin/env python
# -*- coding: utf-8 -*-
import peewee
from services import celery
from utils.log import app_logger
from . import notify_modules
from models.message import Message
from models import model2dict
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


def get_message(id=None, order_by='id', order_type='desc', to_dict=True):
    '''查询数据库message记录'''
    if id:
        data = Message.select().where(Message.id == id,
                                      Message.is_deleted == 0).first()
    else:
        order_field = getattr(Message, order_by)
        if order_type.lower() == 'asc':
            data = Message.select().where(
                Message.is_deleted == 0).order_by(-order_field)
        else:
            data = Message.select().where(
                Message.is_deleted == 0).order_by(+order_field)
    if to_dict:
        if isinstance(data, peewee.SelectQuery):
            data = [model2dict(i) for i in data]
        else:
            data = model2dict(data)
    return data


def add_message(message, to_dict=True):
    data = Message.create(message=message)
    if to_dict:
        data = model2dict(data)
    return data


def delete_message(id, real=False):
    if real:
        query = Message.delete().where(Message.id == id)
    else:
        query = Message.update(is_deleted=True).where(Message.id == id)
    count = query.execute()
    data = {'deleted_count': count}
    return data


def update_message(id, send_status=None, is_deleted=None, to_dict=True):
    data = Message.select().where(Message.id == id).first()
    if not data:
        return
    if send_status is not None:
        data.send_status = send_status
    if is_deleted is not None:
        data.is_deleted = is_deleted
    data.save()
    if to_dict:
        data = model2dict(data)
    return data
