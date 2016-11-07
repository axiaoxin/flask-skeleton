import os
import sys
from multiprocessing import cpu_count

root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
app_path = os.path.join(root_path, 'app')
sys.path.append(app_path)
import settings  # noqa

proc_name = settings.SERVICE_NAME
bind = settings.API_BIND
workers = cpu_count()
worker_class = 'gevent'
reload = settings.DEBUG
pidfile = os.path.join(settings.PROJECT_ROOT_PATH, 'deploy', 'supervisor',
                       'pids', proc_name + '.pid')
raw_env = []
pythonpath = ','.join([app_path, root_path])
loglevel = settings.LOG_LEVEL
access_log_format = '%(t)s %(h)s "%(f)s" "%(a)s" "%(r)s" %(s)s %(p)s %(L)s'
accesslog = os.path.join(settings.LOG_PATH, 'gunicorn.log')
errorlog = os.path.join(settings.LOG_PATH, 'gunicorn.log')
