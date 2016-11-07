#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
通知引擎SDK编写必须按照以下规范：
1. 实现send_email,send_sms,...方法
2. 以上实现方法的返回值为 (RetCode, result)，result为发送接口的返回值
3. 以上实现方法参数顺序必须为func(send_to, title, content)
4. 必须定义allowed列表，将以上方法名称加入allowed列表用于参数验证
'''

import glob
import os
import importlib


def get_engine_module_names():
    current_path = os.path.dirname(os.path.realpath(__file__))
    excludes = ['__init__.py']
    return [os.path.splitext(os.path.basename(filename))[0]
            for filename in glob.glob(os.path.join(current_path, '*.py'))
            if os.path.basename(filename) not in excludes]


def import_module(module_name):
    module = 'apis.demo.notify_modules.%s' % module_name
    return importlib.import_module(module)
