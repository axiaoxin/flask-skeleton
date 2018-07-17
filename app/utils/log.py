#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import sys
import time
from functools import wraps
from logging import Logger, raiseExceptions
from logging.handlers import TimedRotatingFileHandler

import settings
import utils
from services import sentry


class SplitLogger(Logger):
    def __init__(self, name, level=logging.NOTSET):
        super(SplitLogger, self).__init__(name, level)

    def callHandlers(self, record):
        """
        Pass a record to all relevant handlers.

        Loop through all handlers for this logger and its parents in the
        logger hierarchy. If no handler was found, output a one-off error
        message to sys.stderr. Stop searching up the hierarchy whenever a
        logger with the "propagate" attribute set to zero is found - that
        will be the last logger whose handlers are called.
        """
        c = self
        found = 0
        while c:
            for hdlr in c.handlers:
                found = found + 1
                if hdlr.name == 'console':
                    if record.levelno >= hdlr.level:
                        hdlr.handle(record)
                else:
                    if record.levelno == hdlr.level:
                        hdlr.handle(record)
            if not c.propagate:
                c = None  # break out
            else:
                c = c.parent
        if (
                found == 0
        ) and raiseExceptions and not self.manager.emittedNoHandlerWarning:  # noqa
            sys.stderr.write("No handlers could be found for logger"
                             " \"%s\"\n" % self.name)
            self.manager.emittedNoHandlerWarning = 1


class RequestIDLogFilter(logging.Filter):
    """
    Log filter to inject the current request id of the request
    under `log_record.request_id`
    """

    def filter(self, log_record):
        from utils import request
        log_record.request_id = request.current_request_id()
        return log_record


def init_logger(logger_name,
                logging_level=settings.LOG_LEVEL,
                log_in_file=settings.LOG_IN_FILE,
                logfile_name=settings.SERVICE_NAME,
                log_path=settings.LOG_PATH,
                split_logfile_by_level=settings.SPLIT_LOGFILE_BY_LEVEL):

    formatter = logging.Formatter(
        '[%(asctime)s] [%(process)d] [%(levelname)s] [%(request_id)s] %(message)s')  # noqa

    if log_in_file:
        if split_logfile_by_level:
            logging.setLoggerClass(SplitLogger)
            logger = logging.getLogger(logger_name)
            level = logging.getLevelName(logging_level.upper())
            logger.setLevel(level)

            log_files = {
                logging.DEBUG:
                os.path.join(log_path, logfile_name + '.debug.log'),
                logging.INFO:
                os.path.join(log_path, logfile_name + '.info.log'),
                logging.WARNING:
                os.path.join(log_path, logfile_name + '.warning.log'),
                logging.ERROR:
                os.path.join(log_path, logfile_name + '.error.log'),
            }

            for log_level, log_file in log_files.items():
                file_handler = TimedRotatingFileHandler(log_file, 'midnight',
                                                        1, 7)
                file_handler.setLevel(log_level)
                file_handler.setFormatter(formatter)
                file_handler.addFilter(RequestIDLogFilter())
                logger.addHandler(file_handler)
        else:
            logger = logging.getLogger(logger_name)
            level = logging.getLevelName(logging_level.upper())
            logger.setLevel(level)
            log_file = os.path.join(log_path, logfile_name + '.log')
            file_handler = TimedRotatingFileHandler(log_file, 'midnight', 1, 7)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            file_handler.addFilter(RequestIDLogFilter())
            logger.addHandler(file_handler)

    logger = logging.getLogger(logger_name)
    level = logging.getLevelName(logging_level.upper())
    logger.setLevel(level)
    console_handler = logging.StreamHandler()
    console_handler.name = "console"
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestIDLogFilter())
    logger.addHandler(console_handler)

    return logger


app_logger = init_logger(settings.SERVICE_NAME)
if settings.LOG_PEEWEE_SQL:
    pw_logger = init_logger('peewee', logging_level='DEBUG')


def _capture_exception_for_sentry(log_func):
    def decorator(msg, *args, **kwargs):
        log_func(msg, *args, **kwargs)
        if isinstance(msg, Exception):
            sentry.captureException()
    return decorator


app_logger.debug = _capture_exception_for_sentry(app_logger.debug)
app_logger.info = _capture_exception_for_sentry(app_logger.info)
app_logger.warning = _capture_exception_for_sentry(app_logger.warning)
app_logger.error = _capture_exception_for_sentry(app_logger.error)
app_logger.critical = _capture_exception_for_sentry(app_logger.critical)
app_logger.exception = _capture_exception_for_sentry(app_logger.exception)


def _log_func_call(func, use_time, *func_args, **func_kwargs):
    arg_names = func.func_code.co_varnames[:func.func_code.co_argcount]
    args = func_args[:len(arg_names)]
    defaults = func.func_defaults or ()
    args = args + defaults[len(defaults) - (func.func_code.co_argcount - len(
        args)):]
    params = zip(arg_names, args)
    args = func_args[len(arg_names):]
    if args:
        params.append(('args', args))
    if func_kwargs:
        params.append(('kwargs', func_kwargs))
    func_name = utils.get_func_name(func)
    func_call = u'{func_name}({params}) {use_time}ms'.format(
        func_name=func_name,
        params=', '.join('%s=%r' % p for p in params),
        use_time=use_time * 1000)
    if use_time * 1000 > settings.CACHED_OVER_EXEC_MILLISECONDS:
        app_logger.warning(func_call)
    else:
        app_logger.info(func_call)


def log_func_call(func):
    '''Decorator to log function call'''

    @wraps(func)
    def wrapper(*func_args, **func_kwargs):
        if settings.LOG_FUNC_CALL:
            start_time = time.time()
            data = func(*func_args, **func_kwargs)
            use_time = time.time() - start_time
            _log_func_call(func, use_time, *func_args, **func_kwargs)
            return data
        return func(*func_args, **func_kwargs)

    return wrapper
