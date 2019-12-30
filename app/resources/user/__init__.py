from flask import Blueprint

from app.resources.user.channel import UserChannelResource
from app.resources.user.passport import SMSCodeResource, LoginResource
from app.resources.user.profile import CurrentUserResource
from utils.constants import USER_URL_PREFIX
from flask_restful import Api

# 创建蓝图对象
user_bp = Blueprint('user_bp', __name__, url_prefix=USER_URL_PREFIX)

# 创建Api对象
user_api = Api(user_bp)

# 设置json包装格式
from utils.output import output_json
user_api.representation('application/json')(output_json)

# 用api注册路由
user_api.add_resource(SMSCodeResource, '/sms/codes/<mob:mobile>')
user_api.add_resource(LoginResource, '/authorizations')
user_api.add_resource(CurrentUserResource, '/user')
user_api.add_resource(UserChannelResource, '/user/channels')
