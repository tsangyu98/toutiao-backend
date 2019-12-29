from flask import Flask
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'common'))

from app.settings.config import config_dict
from utils.constants import EXTRA_ENV_CONFIG
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis


db = SQLAlchemy()
redis_cli = None


def create_flask_app(type):
    """创建flask应用"""

    # 创建flask应用
    app = Flask(__name__)
    # 根据类型加载配置子类
    config_class = config_dict[type]
    # 先加载默认配置
    app.config.from_object(config_class)
    # 再加载额外配置
    app.config.from_envvar(EXTRA_ENV_CONFIG, silent=True)
    # 返回应用
    return app


def register_extensions(app):
    """组件初始化"""
    # mysql组件初始化
    db.init_app(app)
    # Redis配置
    global redis_cli
    redis_cli = StrictRedis(host=app.config['REDIS_LOCATION'], port=app.config['REDIS_PORT'])



def create_app(type):
    """创建应用和组件化"""
    # 创建flask应用
    app = create_flask_app(type)
    # 组件初始化
    register_extensions(app)
    # 返回应用
    return app
