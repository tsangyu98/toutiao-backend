from flask import request, g, jsonify
from utils.jwt_util import verify_jwt


def get_user_info():
    """获取用户信息"""
    # 获取请求头的token
    header = request.headers.get('Authorization')

    g.userid = None  # 如果未登录，userid=None
    if header and header.startswith('Bearer'):
        # 取出token
        token = header[7:]
        # 校验token
        data = verify_jwt(token)
        if data:
            # 校验成功
            g.userid = data.get('userid')  # 如果已登录, userid=11
