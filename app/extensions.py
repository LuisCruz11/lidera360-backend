from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["300 per hour"],
)


@limiter.request_filter
def _exentar_preflight():
    return request.method == "OPTIONS"
