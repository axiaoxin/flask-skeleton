from flask.views import MethodView
from utils import cache, log


view_decorators = [cache.cached_call(namespace='views'), log.log_func_call]
handler_decorators = [log.log_func_call]


class BaseView(MethodView):
    decorators = view_decorators
