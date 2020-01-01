from flask import g
from flask_restful import Resource
from flask_restful.inputs import regex

from models import db
from models.article import Comment, Article
from models.user import User
from utils.decorators import login_required
from flask_restful.reqparse import RequestParser

class CommentsResource(Resource):
    method_decorators = {'post': [login_required]}

    def post(self):
        """发布评论"""
        # 接收参数
        userid = g.userid
        parser = RequestParser()
        parser.add_argument('target', required=True, location='json', type=int)
        parser.add_argument('content', required=True, location='json', type=regex(r'.+'))
        parser.add_argument('parent_id', default=0, location='json', type=int)
        args = parser.parse_args()
        # 文章id
        article_id = args.target
        # 评论内容
        content = args.content
        # 父评论id
        parent_id = args.parent_id

        if parent_id:
            # 生成子评论
            comment = Comment(user_id=userid, article_id=article_id, content=content, parent_id=parent_id)
            db.session.add(comment)
            # 让评论的子评论数+1
            Comment.query.filter(Comment.id == parent_id).update({'reply_count': Comment.reply_count + 1})
        else:
            # 生成父评论记录
            comment = Comment(user_id=userid, article_id=article_id, content=content, parent_id=0)
            db.session.add(comment)
            # 让文章的评论数+1
            Article.query.filter(Article.id == article_id).update({'comment_count': Article.comment_count + 1})

        db.session.commit()

        # 返回结果
        return {"com_id": comment.id, "target": article_id}

    def get(self):
        """获取评论列表"""
        # 获取参数
        parser = RequestParser()
        parser.add_argument('source', required=True, location='args', type=int)
        parser.add_argument('offset', default=0, location='args', type=int)
        parser.add_argument('limit', default=10, location='args', type=int)
        parser.add_argument('type', required=True, location='args', type=regex(r'[ac]'))
        args = parser.parse_args()

        # 文章的id
        article_id = args.source
        # 评论数据的偏移量
        offset = args.offset
        # 获取的评论条数
        limit = args.limit
        # 请求的数据类型  a 评论列列表 c 回复列列表
        type = args.type

        # 查询文章的评论数据
        if type == 'a':
            # 评论列表
            comments = db.session.query(Comment.id, Comment.user_id, User.name, User.profile_photo, Comment.ctime, Comment.content, Comment.reply_count, Comment.like_count).\
                join(User, Comment.user_id == User.id).filter(Comment.article_id == article_id, Comment.parent_id == 0, Comment.id > offset).limit(limit).all()

            # 查询评论总数
            total_count = Comment.query.filter(Comment.article_id == article_id, Comment.parent_id == 0).count()

            # 所有评论中的最后一个id
            end_comment = db.session.query(Comment.id).filter(Comment.article_id == article_id, Comment.parent_id == 0).order_by(Comment.id.desc()).first()
        else:
            # 回复列列表
            comments = db.session.query(Comment.id, Comment.user_id, User.name, User.profile_photo, Comment.ctime,
                                        Comment.content, Comment.reply_count, Comment.like_count). \
                join(User, Comment.user_id == User.id).filter(Comment.article_id == article_id,
                                                              Comment.id > offset).limit(limit).all()
            # 查询评论总数
            total_count = Comment.query.filter(Comment.article_id == article_id).count()
            # 所有评论中的最后一个id
            end_comment = db.session.query(Comment.id).filter(Comment.article_id == article_id).order_by(Comment.id.desc()).first()

        # 所有评论中的最后一个id
        end_id = end_comment.id if end_comment else None

        # 本次请求的最后一个id
        last_id = comments[-1].id if comments else None

        # 序列化
        results = [{"com_id": comment.id,
                    "aut_id": comment.user_id,
                    "aut_name": comment.name,
                    "aut_photo": comment.profile_photo,
                    "pubdate": comment.ctime.isoformat(),
                    "content": comment.content,
                    "reply_count": comment.reply_count,
                    "like_count": comment.like_count} for comment in comments]

        # 返回响应
        return {"results": results, "total_count": total_count, "end_id": end_id, "last_id": last_id}





