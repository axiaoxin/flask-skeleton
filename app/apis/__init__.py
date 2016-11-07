from flask.views import MethodView
from cerberus import Validator
# http://docs.python-cerberus.org/en/stable/validation-rules.html
from utils import cache, log

validator = Validator()

view_decorators = [cache.cached_call(namespace='views'), log.log_func_call]
handler_decorators = [log.log_func_call]


class BaseView(MethodView):
    decorators = view_decorators
