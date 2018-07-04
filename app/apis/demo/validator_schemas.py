#!/usr/bin/env python
# -*- coding: utf-8 -*-
from . import notify_modules

notify_module = notify_modules.import_module('tof')

message_entry_data = {

    'caller_id': {
        'type': 'integer',
        'empty': False,
        'required': True,
    },

    'caller_key': {
        'type': 'string',
        'empty': False,
        'required': True,
    },

    'notify_method': {
        'type': 'string',
        'empty': False,
        'allowed': getattr(notify_module, 'allowed'),
        'required': True,
    },

    'send_to': {
        'type': 'list',
        'empty': False,
        'required': True,
    },

    'title': {
        'type': 'string',
        'maxlength': 128,
        'empty': False,
        'required': True,
    },

    'content': {
        'type': 'string',
        'empty': False,
        'required': True,
    },

    'async': {
        'type': 'boolean',
        'empty': False,
        'required': False,
    },
}
