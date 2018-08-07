#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint

from . import views

message_api = Blueprint('message', __name__)

# 消息入口
message_api.add_url_rule('/entry', view_func=views.EntryView.as_view('entry'))
# 查询任务状态
message_api.add_url_rule(
    '/notify_task/<task_id>',
    view_func=views.NotifyTaskView.as_view('notify_task'))
# 查询消息发送结果
message_api.add_url_rule(
    '/notify_status/<task_id>',
    view_func=views.NotifyStatusView.as_view('notify_status'))

# 数据库操作
records_view = views.RecordsView.as_view('records')
message_api.add_url_rule(
    '/records', view_func=records_view,
    methods=['GET', 'POST'])  # methods for flasgger
message_api.add_url_rule(
    '/records/<int:id>',
    view_func=records_view,
    methods=['GET', 'DELETE', 'PUT'])
