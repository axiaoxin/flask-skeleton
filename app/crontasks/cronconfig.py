import sys
from celery.schedules import crontab
from decouple import config
sys.path.append('..')  # noqa
import settings

broker_url = config('BROKER_URL', default=settings.BROKER_URL)

result_backend = config(
    'CELERY_RESULT_BACKEND', default=settings.CELERY_RESULT_BACKEND)

timezone = 'Asia/Shanghai'

imports = ['tasks.demo', ]

beat_schedule = {
    'print-arg-every-1-seconds': {
        'task': 'tasks.demo.print_arg',
        'schedule': 1,
        'args': ('hello', )
    },
    'print-args-every-1-minutes': {
        'task': 'tasks.demo.print_args',
        'schedule': crontab(minute='*/1'),
        'args': ('world', )
    },
}
