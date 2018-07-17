# -*- coding:utf-8 -*-
__repo__ = 'https://github.com/axiaoxin/flask-skeleton'
__version__ = '0.0.1'
__author__ = 'axiaoxin'

import os  # noqa
from ast import literal_eval  # noqa
from multiprocessing import cpu_count  # noqa

from decouple import config  # noqa

########################
# settings for project #
########################

DEBUG = config('DEBUG', default=False, cast=bool)

APP_ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
PROJECT_ROOT_PATH = os.path.dirname(APP_ROOT_PATH)

SERVICE_NAME = config('SERVICE_NAME', default='flask-skeleton')
API_BIND = config('API_URL', default='localhost:5000')

JSON_AS_ASCII = config('JSON_AS_ASCII', default=False, cast=bool)
JSON_KEYCASE = config('JSON_KEYCASE', default=None)

EXCEPTION_RETRY_COUNT = config('EXCEPTION_RETRY_COUNT', default=2, cast=int)

FAKE_HANDLE_TASK = config('FAKE_HANDLE_TASK', default=False, cast=bool)

REQUESTS_POOL_SIZE = config('REQUESTS_POOL_SIZE', default=10, cast=int)

REQUEST_ID_KEY = config('REQUEST_ID_KEY', default='X-Request-ID')

####################
# settings for log #
####################

LOG_PATH = config("LOG_PATH", default=os.path.join(PROJECT_ROOT_PATH, 'logs'))
LOG_LEVEL = config('LOG_LEVEL', default='debug')
LOG_FUNC_CALL = config('LOG_FUNC_CALL', default=True, cast=bool)
LOG_PEEWEE_SQL = config('LOG_PEEWEE_SQL', default=False, cast=bool)
LOG_IN_FILE = config('LOG_IN_FILE', default=False, cast=bool)
SPLIT_LOGFILE_BY_LEVEL = config(
    'SPLIT_LOGFILE_BY_LEVEL', default=False, cast=bool)

SENTRY_DSN = config(
    'SENTRY_DSN',
    default=''  # noqa
)

#########################
# settings for database #
#########################

MYSQL_URL = config(
    'MYSQL_URL',
    default='mysql+pool://root:root@localhost:3306/test?max_connections=40&stale_timeout=300'  # noqa
)

######################
# settings for redis #
######################

# if set REDIS_CLUSTER, REDIS_URL and REDIS_SENTINEL are invalid.
# if not set REDIS_CLUSTER and set REDIS_SENTINEL, just using redis sentinel
# if want to use REDIS_URL, just set REDIS_URL

REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CACHED_CALL = config('CACHED_CALL', default=False, cast=bool)
CACHED_OVER_EXEC_MILLISECONDS = config(
    'CACHED_OVER_EXEC_MILLISECONDS', default=800, cast=int)
CACHED_EXPIRE_SECONDS = config('CACHED_EXPIRE_SECONDS', default=60, cast=int)
REDIS_LOCK_TIMEOUT = config('REDIS_LOCK_TIMEOUT', default=1800, cast=int)
# sentinel example:
# {
#    'nodes': [('localhost', 26379)],
#    'master_name': 'mymaster',
#    'socket_timeout': 0.1,
#    'db': 0,
#    'password': 'password'
# }
REDIS_SENTINEL = config(
    'REDIS_SENTINEL',
    default={},
    cast=lambda x: x if not x else literal_eval(x))
# cluster example:
# {
#   'nodes': [{"host": "127.0.0.1", "port": "6379"}],
#   'password': 'password'
# }
REDIS_CLUSTER = config(
    'REDIS_CLUSTER',
    default={},
    cast=lambda x: x if not x else literal_eval(x))

#######################
# settings for celery #
#######################

# rabbitmq operate:
# ./rabbitmqctl add_user username password
# ./rabbitmqctl set_user_tags username administrator
# ./rabbitmqctl add_vhost vhostname
# ./rabbitmqctl set_permissions -p vhostname username ".*" ".*" ".*"

CELERY_TIMEZONE = config('CELERY_TIMEZONE', default='Asia/Shanghai')
BROKER_URL = config(
    'BROKER_URL',
    default='amqp://guest:guest@localhost:5672//'  # noqa
)
# using redis sentinel for backend
# set -> sentinel://:password@ip1:26379/db;sentinel://:password@ip2:26379/db
CELERY_RESULT_BACKEND = config(
    'CELERY_RESULT_BACKEND', default='redis://localhost:6379/1')
# using redis sentinel for backend must set the master_name
CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = {
    'master_name': config(
        'REDIS_SENTINEL_MASTER_NAME', default='')
}
CELERY_RESULT_PERSISTENT = config(
    'CELERY_RESULT_PERSISTENT', default=True, cast=bool)
CELERY_TASK_RESULT_EXPIRES = config(
    'CELERY_TASK_RESULT_EXPIRES', default=60 * 60 * 24 * 7, cast=int)
CELERYD_TASK_SOFT_TIME_LIMIT = config(
    'CELERYD_TASK_SOFT_TIME_LIMIT', default=30, cast=int)
CELERYD_MAX_TASKS_PER_CHILD = config(
    'CELERYD_MAX_TASKS_PER_CHILD', default=10000, cast=int)
CELERYD_CONCURRENCY = config(
    'CELERYD_CONCURRENCY', default=cpu_count(), cast=int)
CELERYD_SEND_EVENTS = config('CELERYD_SEND_EVENTS', default=True, cast=bool)

########################
# settings for swagger #
########################

SWAGGER = {
    'title': '%s API' % SERVICE_NAME,
    'uiversion': 3,
    'doc_expansion': 'list',  # none|full
    'version': __version__,
    'footer_text': u'有任何疑问请咨询 %s' % __author__,
    'termsOfService': None,
    'specs': [
        {
            'endpoint': 'apispec',
            'route': '/apispec.json'
        }
    ],
    'hide_top_bar': False,
    'description': '<a href="/docs">其他文档</a>'
}

##########################
# settings for flatpages #
##########################

FLATPAGES_ROOT = os.path.join(PROJECT_ROOT_PATH, 'docs')
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = ['.md', '.html', '.htm', '.txt']
