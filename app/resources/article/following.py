from flask import g
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import load_only

from models import db
from models.user import Relation, User
from utils.decorators import login_required


class FollowUserResource(Resource):
    """用户关注接口"""
    method_decorators = {"post": [login_required]}

    def post(self):
        """关注用户接口"""
        userid = g.userid

        parser = RequestParser()
        parser.add_argument('target', required=True, location='json', type=int)
        args = parser.parse_args()

        aut_id = args.target

        #  # 第一种方式
        # 查询数据
        # relation = Relation.query.options(load_only(Relation.id)).filter(Relation.user_id == userid, Relation.target_user_id == aut_id).first()

        # # 如果有，修改记录
        # if relation:
        #     relation.relation = Relation.RELATION.FOLLOW
        # # 如果没有，则添加数据
        # else:
        #     relation = Relation(user_id=userid, target_user_id=aut_id, relation=Relation.RELATION.FOLLOW)
        #     db.session.add(relation)
        # db.session.commit()

        # 第二种方式
        update_statement = insert(Relation).values([{'user_id': userid, 'target_user_id': aut_id, 'relation': Relation.RELATION.FOLLOW}]).on_duplicate_key_update(relation=Relation.RELATION.FOLLOW)
        # 执行sql
        db.session.execute(update_statement)
        # 提交事务
        db.session.commit()

        # 返回结果
        return {'target': aut_id}

    def get(self):
        """获取用户关注列表"""
        # 获取参数
        userid = g.userid
        parser = RequestParser()
        parser.add_argument('page', required=True, location='args', type=int)
        parser.add_argument('per_page', default=2, location='args', type=int)
        args = parser.parse_args()
        # 页码
        page = args.page
        # 每页条数
        per_page = args.per_page

        # 查询数据
        pn = User.query.options(load_only(User.id, User.name, User.profile_photo, User.fans_count)).join(Relation, User.id == Relation.target_user_id).filter(Relation.user_id == userid, Relation.relation == Relation.RELATION.FOLLOW).\
            order_by(Relation.update_time.desc()).paginate(page, per_page, error_out=False)
        # 序列化
        results = [{"id": item.id, "name": item.name, "photo": item.profile_photo, "fans_count": item.fans_count, "mutual_follow": False} for item in pn.items]
        # 返回数据
        return {'results': results, 'total_count': pn.total, 'page': pn.page, 'per_page': per_page}






class UnFollowUserResource(Resource):
    """取消关注接口"""
    method_decorators = {'post': [login_required]}

    def delete(self, target):
        # 获取参数
        userid = g.userid

        Relation.query.filter(Relation.user_id == userid, Relation.target_user_id == target, Relation.relation == Relation.RELATION.FOLLOW).update({'relation': 0})
        db.session.commit()
        # 返回数据
        return {'target': target}

