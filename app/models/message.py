#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

import peewee

from models import MySQLBaseModel


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
