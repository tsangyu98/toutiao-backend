from flask import g
from functools import wraps


def login_required(f):
    def wrapper(*args, **kwargs):
        # 如果用户已登录，正常访问
        if g.userid:
            return f(*args, **kwargs)
        else:
            return {'message': 'Invalid Token', 'data': None}, 401

    return wrapper
