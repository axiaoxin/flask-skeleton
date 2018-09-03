#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import request
from utils import validate_dict, pagination
from utils.response import response
from utils.response import RetCode, RetCodeMsg
from apis import handler_decorators, BaseView
from . import validator_schemas
from . import handlers
from services import peewee_mysql
import utils

# 为handlers里面的函数注册装饰器
utils.register_decorators_on_module_funcs(handlers, handler_decorators)


class EntryView(BaseView):
    def post(self):
        '''消息入口
        异步发送接收到的通知消息，返回task_id
        ---
        tags:
          - notify.demo
        definitions:
          entry_body:
            type: object
            required: [caller_id, caller_key, notify_method,
                       send_to, title, content]
            properties:
              caller_id:
                type: integer
                description: 调用方id
                example: 1
              caller_key:
                type: string
                description: 调用方key
                example: key
              notify_method:
                type: string
                description: 通知方法
                example: send_email
              send_to:
                type: array
                description: 通知人列表
                items:
                  type: string
                example: ["axiaoxin"]
              title:
                type: string
                description: 通知消息标题
                example: 红头文件
              content:
                type: string
                description: 通知消息内容
                example: 你已被任命为CEO
              async:
                type: boolean
                description: 使用异步任务发送
                example: true
          response:
            type: object
            properties:
              code:
                type: integer
              msg:
                type: string
              data:
                type: object
        parameters:
          - name: entry_body
            in: body
            required: true
            description: 请求体为通知消息JSON数据
            schema:
              $ref: '#/definitions/entry_body'
        responses:
          200:
            description: 接口返回JSON数据
            schema:
              $ref: '#/definitions/response'
            examples:
              成功: {"code": 0, "msg": "SUCCESS", "data": null}
              失败: {"code": -1, "msg": "FAILURE", "data": null}
              参数错误: {"code": 400, "msg": "PARAMS ERROR", "data": null}
              资源不存在: {"code": 404, "msg": "ENTITY NOT FOUND", "data": null}
              服务器错误: {"code": 500, "msg": "INTERNAL SERVER ERROR",
                           "data": null}
        '''
        data = request.get_json() or {}
        validate_dict(data, validator_schemas.message_entry_data)
        async = data.get('async', True)
        if async is True:
            task = handlers.handle_message(data)
            return response({'task_id': task.id})
        else:
            retcode, result = handlers.notify(data)
            return response(code=retcode, data=result)


class NotifyTaskView(BaseView):
    def get(self, task_id):
        '''获取任务
        根据task_id查询任务信息
        ---
        tags:
          - notify.demo
        parameters:
          - name: task_id
            in: path
            type: string
            required: true
            description: The task_id
        responses:
          200:
            description: 接口返回JSON数据
            schema:
              $ref: '#/definitions/response'
            examples:
              成功: {"code": 0, "msg": "SUCCESS", "data": null}
              失败: {"code": -1, "msg": "FAILURE", "data": null}
              参数错误: {"code": 400, "msg": "PARAMS ERROR", "data": null}
              资源不存在: {"code": 404, "msg": "ENTITY NOT FOUND", "data": null}
              服务器错误: {"code": 500, "msg": "INTERNAL SERVER ERROR",
                           "data": null}
        '''
        task = handlers.get_notify_task(task_id)
        result = {
            'status': task.status,
            'result': task.result,
            'traceback': task.traceback
        }
        return response(result)


class NotifyStatusView(BaseView):
    def get(self, task_id):
        """查询消息发送状态
        根据task_id查询对应消息的发送状态
        ---
        tags:
          - notify.demo
        parameters:
          - name: task_id
            in: path
            required: true
            type: string
            description: The task_id
        responses:
          200:
            description: 接口返回JSON数据
            schema:
              $ref: '#/definitions/response'
            examples:
              成功: {"code": 0, "msg": "SUCCESS", "data": null}
              失败: {"code": -1, "msg": "FAILURE", "data": null}
              参数错误: {"code": 400, "msg": "PARAMS ERROR", "data": null}
              资源不存在: {"code": 404, "msg": "ENTITY NOT FOUND", "data": null}
              服务器错误: {"code": 500, "msg": "INTERNAL SERVER ERROR",
                           "data": null}
        """
        task_id = request.values['task_id']
        task = handlers.get_notify_task(task_id)

        if task.state == 'SUCCESS' and task.result:
            retcode, result = task.result
            status = RetCodeMsg.get(retcode)
            data = {'status': status, 'result': result}
        else:
            data = {
                'status': task.status,
                'result': task.result,
                'traceback': task.traceback
            }
            retcode = RetCode.FAILURE

        return response(data, retcode)


class RecordsView(BaseView):
    @peewee_mysql.connection_context()
    def get(self, id=None):
        """查
        根据db主键id查询对应记录
        ---
        tags:
          - db.demo
        parameters:
          - name: id
            in: path
            required: false
            type: integer
            description: URL endswith id will query singel record,
                no id query all records.
        responses:
          200:
            description: 接口返回JSON数据
            schema:
              $ref: '#/definitions/response'
            examples:
              成功: {"code": 0, "msg": "SUCCESS", "data": null}
              失败: {"code": -1, "msg": "FAILURE", "data": null}
              参数错误: {"code": 400, "msg": "PARAMS ERROR", "data": null}
              资源不存在: {"code": 404, "msg": "ENTITY NOT FOUND", "data": null}
              服务器错误: {"code": 500, "msg": "INTERNAL SERVER ERROR",
                           "data": null}
        """
        if id is None:
            page_num = int(request.values.get('page_num', 1))
            page_size = int(request.values.get('page_size', 10))
            order_by = request.values.get('order_by', 'id')
            order_type = request.values.get('order_type', 'desc')
            send_status = request.values.get('send_status')
            items = handlers.get_message(
                order_by=order_by,
                order_type=order_type,
                page_num=page_num,
                page_size=page_size,
                send_status=send_status)
            items_count = handlers.get_message_count(send_status)
            data = {'items': items,
                    'pagination': pagination(items_count, page_num, page_size)}
        else:
            data = handlers.get_message(id)
        return response(data)

    def post(self):
        """增
        新增db记录
        ---
        tags:
          - db.demo
        parameters:
          - name: body
            in: body
            required: true
            type: object
            description: Content of message field in table
        responses:
          200:
            description: 接口返回JSON数据
            schema:
              $ref: '#/definitions/response'
            examples:
              成功: {"code": 0, "msg": "SUCCESS", "data": null}
              失败: {"code": -1, "msg": "FAILURE", "data": null}
              参数错误: {"code": 400, "msg": "PARAMS ERROR", "data": null}
              资源不存在: {"code": 404, "msg": "ENTITY NOT FOUND", "data": null}
              服务器错误: {"code": 500, "msg": "INTERNAL SERVER ERROR",
                           "data": null}
        """
        # 除了使用装饰器管理连接，也可以用with语句。
        # 使用with db对象除了可以管理连接，还能开启一个事务
        with peewee_mysql:
            data = request.get_json()
            validate_dict(data, validator_schemas.message_entry_data)
            data = handlers.add_message(data)
            return response(data)

    def delete(self, id):
        """删
        根据id删除db记录
        ---
        tags:
          - db.demo
        parameters:
          - name: id
            in: path
            required: true
            type: integer
            description: Primary key id
        responses:
          200:
            description: 接口返回JSON数据
            schema:
              $ref: '#/definitions/response'
            examples:
              成功: {"code": 0, "msg": "SUCCESS", "data": null}
              失败: {"code": -1, "msg": "FAILURE", "data": null}
              参数错误: {"code": 400, "msg": "PARAMS ERROR", "data": null}
              资源不存在: {"code": 404, "msg": "ENTITY NOT FOUND", "data": null}
              服务器错误: {"code": 500, "msg": "INTERNAL SERVER ERROR",
                           "data": null}
        """
        with peewee_mysql:
            data = handlers.delete_message(id)
            return response(data)

    def put(self, id):
        """改
        修改对应id记录的send_status字段为fail状态
        ---
        tags:
          - db.demo
        parameters:
          - name: id
            in: path
            required: true
            type: integer
            description: Primary key id
        responses:
          200:
            description: 接口返回JSON数据
            schema:
              $ref: '#/definitions/response'
            examples:
              成功: {"code": 0, "msg": "SUCCESS", "data": null}
              失败: {"code": -1, "msg": "FAILURE", "data": null}
              参数错误: {"code": 400, "msg": "PARAMS ERROR", "data": null}
              资源不存在: {"code": 404, "msg": "ENTITY NOT FOUND", "data": null}
              服务器错误: {"code": 500, "msg": "INTERNAL SERVER ERROR",
                           "data": null}
        """
        with peewee_mysql:
            from models.message import Message
            data = handlers.update_message(
                id, send_status=Message.SEND_FAILURE)
            return response(data)
