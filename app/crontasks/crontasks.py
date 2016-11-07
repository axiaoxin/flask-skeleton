#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from celery import Celery
from celery.utils.log import get_task_logger
from raven import Client
from raven.contrib.celery import register_signal, register_logger_signal
import sys
sys.path.append('..')  # noqa
import settings

celery = Celery('crontasks')
celery.config_from_object('cronconfig')
logger = get_task_logger(__name__)

sentry = Client(settings.SENTRY_DSN)
register_logger_signal(sentry)
register_logger_signal(sentry, loglevel=logging.INFO)
register_signal(sentry)
register_signal(sentry, ignore_expected=True)


if __name__ == '__main__':
    celery.start()
