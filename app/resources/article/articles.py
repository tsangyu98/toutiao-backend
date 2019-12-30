import datetime

from flask import g
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy.orm import load_only

from models import db
from models.article import Article, ArticleContent, Attitude, Collection
from models.user import User, Relation
from utils.constants import HOME_PER_PAGE


class ArticleListResource(Resource):
    """获取所有文章"""
    def get(self):
        # 获取请求参数
        parser = RequestParser()
        parser.add_argument('channel_id', required=True, location='args', type=int)  # 获取频道id
        parser.add_argument('timestamp', required=True, location='args', type=int)
        args = parser.parse_args()

        # 获取频道id
        channel_id = args.channel_id
        # 获取时间戳
        timestamp = args.timestamp

        # 如果为推荐模块，先返回空数据
        if channel_id == 0:
            return {"results": [], "pre_timestamp": 0}

        # 把timestamp转换为datetime
        date = datetime.datetime.fromtimestamp(timestamp * 0.001)

        # 查询频道中对应的数据
        datas = db.session.query(Article.id, Article.title, Article.user_id, Article.ctime, User.name, Article.comment_count, Article.cover).join(User, Article.user_id == User.id).filter(Article.channel_id == channel_id, Article.status == Article.STATUS.APPROVED, Article.ctime < date).order_by(Article.ctime.desc()).limit(HOME_PER_PAGE).all()

        # 序列化
        articles = [{'art_id': data.id, 'title': data.title, 'aut_id': data.user_id, 'pubdate': data.ctime.isoformat(), 'aut_name':data.name, 'comm_count': data.comment_count, 'cover': data.cover} for data in datas]

        # 设置pre_timestamp
        pre_timestamp = datas[-1].ctime.timestamp() * 1000 if datas else 0

        # 返回数据
        return {"results": articles, "pre_timestamp": pre_timestamp}


class ArticleDetailResource(Resource):
    """获取文章详情接口"""
    def get(self, article_id):
        # 获取参数
        userid = g.userid

        # 查询数据
        data = db.session.query(Article.id, Article.title, Article.ctime, Article.user_id, User.name, User.profile_photo, ArticleContent.content).join(User, Article.user_id == User.id).join(Article.id == ArticleContent.id).filter(Article.id == article_id).first()

        # 序列化
        article_dict = {
            "art_id": data.id,
            "title": data.title,
            "pubdate": data.ctime.isoformat(),
            "aut_id": data.user_id,
            "aut_name": data.name,
            "aut_photo": data.profile_photo,
            "content": data.content,
            "is_followed": False,
            "attitude": -1,  # 不不喜欢0 喜欢1 ⽆无态度-1
            "is_collected": False
        }


        # 判断用户是否登录
        if userid:
            # 查询用户的关注关系
            relation_obj = Relation.query.options(load_only(Relation.id)).filter(Relation.user_id == userid, Relation.relation == Relation.RELATION.FOLLOW, Relation.target_user_id == data.user_id).first()
            article_dict['is_followed'] = True if relation_obj else False
            # 查询文章点赞情况
            attitude_obj = Attitude.query.options(load_only(Attitude.attitude)).filter(Attitude.user_id == userid, Article.article_id == article_id).first()
            article_dict['attitude'] = attitude_obj.attitude if attitude_obj else -1
            # 查询文章收藏情况
            collection_obj = Collection.query.options(load_only(Collection.id)).filter(Collection.user_id == userid, Collection.article_id == article_id, Collection.is_deleted == False).first()
            article_dict['is_collected'] = True if collection_obj else False


        # 返回数据
        return article_dict

