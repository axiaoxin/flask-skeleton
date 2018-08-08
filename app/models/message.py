#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

import peewee

from models import MySQLBaseModel
from models import model2dict


class Message(MySQLBaseModel):
    SEND_FAILURE = -1
    SEND_PENDING = 0
    SEND_SUCCESS = 1

    id = peewee.PrimaryKeyField()
    # 如果显式定义主键，必须使用主键类型是PrimaryKeyField或主键属性sequence为True，
    # 插入数据后才能得到自增主键值
    # 例如 id = peewee.BigAutoField(primary_key=True, sequence=True)
    message = peewee.TextField()
    send_status = peewee.SmallIntegerField(default=SEND_PENDING)
    is_deleted = peewee.BooleanField(default=False)
    created_at = peewee.DateTimeField(default=datetime.datetime.now)
    updated_at = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = 'message'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(Message, self).save(*args, **kwargs)

    @classmethod
    def get_record(cls,
                   id=None,
                   order_by='id',
                   order_type='desc',
                   to_dict=True):
        if id:
            data = cls.select().where(cls.id == id,
                                      cls.is_deleted == 0).first()
        else:
            order_field = getattr(cls, order_by)
            if order_type.lower() == 'asc':
                data = cls.select().where(
                    cls.is_deleted == 0).order_by(-order_field)
            else:
                data = cls.select().where(
                    cls.is_deleted == 0).order_by(+order_field)
        if to_dict:
            if isinstance(data, peewee.SelectQuery):
                data = [model2dict(i) for i in data]
            else:
                data = model2dict(data)
        return data

    @classmethod
    def add_record(cls, message, to_dict=True):
        data = cls.create(message=message)
        if to_dict:
            data = model2dict(data)
        return data

    @classmethod
    def delete_record(cls, id, real=False):
        if real:
            query = cls.delete().where(cls.id == id)
        else:
            query = cls.update(is_deleted=True).where(cls.id == id)
        count = query.execute()
        data = {'deleted_count': count}
        return data

    @classmethod
    def update_record(cls, id, send_status=None, is_deleted=None,
                      to_dict=True):
        data = cls.select().where(cls.id == id).first()
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
