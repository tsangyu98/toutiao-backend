from datetime import datetime, timedelta

import random
from flask_restful import Resource
from flask_restful.inputs import regex
from flask_restful.reqparse import RequestParser
from flask import request, current_app
from sqlalchemy.orm import load_only

from app import redis_cli
from models import db
from models.user import User
from utils.constants import SMS_CODE_EXPIRE
from utils.jwt_util import generate_jwt
from utils.parser import mobile as mobile_type


class SMSCodeResource(Resource):
    """获取短信验证码"""

    def get(self, mobile):
        # 生成短信验证码
        # rand_num = '%06d' % random.randint(0, 999999)
        rand_num = '123456'
        # 将验证码存入redis
        key = 'app:code:{}'.format(mobile)
        redis_cli.set(key, rand_num, ex=SMS_CODE_EXPIRE)

        # 发送短信验证码  第三方短信平台  celery
        print('短信验证码: "mobile": {}, "code": {}'.format(mobile, rand_num))
        # 返回结果
        return {'mobile': mobile}


class LoginResource(Resource):
    """注册登录接口"""

    def post(self):
        # 接收参数
        parser = RequestParser()
        parser.add_argument('mobile', required=True, location='json', type=mobile_type)
        parser.add_argument('code', required=True, location='json', type=regex(r'^\d{6}$'))
        args = parser.parse_args()

        mobile = args.mobile
        code = args.code

        # 校验短信验证码
        key = 'app:code:{}'.format(mobile)
        # 获取验证码
        real_code = redis_cli.get(key)
        if not real_code or real_code != code:
            # 验证码校验失败
            return {'message': 'Invalid Code', 'data': None}, 400

        # 删除验证码
        # redis_cli.delete(key)

        # 校验成功，查询是否有这个用户
        user = User.query.options(load_only(User.id)).filter(User.mobile == mobile).first()

        # 如果有，取出用户的id，更新最后的登录时间
        if user:
            user.last_login = datetime.now()
        else:  # 如果没有，则创建新用户
            user = User(mobile=mobile, name=mobile, last_login=datetime.now())
            db.session.add(user)
        db.session.commit()

        # 生成jwt
        token = generate_jwt({'userid': user.id},
                             expiry=datetime.utcnow() + timedelta(days=current_app.config['JWT_EXPIRE_DAYS']))

        # 返回结果
        return {'token': token}, 201
