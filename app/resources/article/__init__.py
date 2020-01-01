from flask import Blueprint

from app.resources.article.articles import ArticleListResource, ArticleDetailResource
from app.resources.article.channel import ChannelResource
from app.resources.article.comment import CommentsResource
from app.resources.article.following import FollowUserResource, UnFollowUserResource
from utils.constants import USER_URL_PREFIX
from flask_restful import Api

# 创建蓝图对象
article_bp = Blueprint('article', __name__, url_prefix=USER_URL_PREFIX)

# 创建Api对象
article_api = Api(article_bp)

# 设置json包装格式
from utils.output import output_json

article_api.representation('application/json')(output_json)

# 用api注册路由
article_api.add_resource(ChannelResource, '/channels')
article_api.add_resource(ArticleListResource, '/articles')
article_api.add_resource(ArticleDetailResource, '/articles/<int:article_id>')
article_api.add_resource(FollowUserResource, '/user/followings')
article_api.add_resource(UnFollowUserResource, '/user/followings/<int:target>')
article_api.add_resource(CommentsResource, '/comments')

