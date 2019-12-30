from flask import g, request
from flask_restful import Resource
from sqlalchemy.orm import load_only
from sqlalchemy.dialects.mysql import insert

from models import db
from models.article import UserChannel, Channel


class UserChannelResource(Resource):
    """用户频道"""

    def get(self):
        # 获取用户信息
        userid = g.userid

        # 判断用户已登录，查询用户频道
        if userid:
            # 查询用户关注的频道
            channels = Channel.query.options(load_only(Channel.id, Channel.name)).join(UserChannel, Channel.id == UserChannel.channel_id).filter(UserChannel.user_id == userid, UserChannel.is_deleted == False).order_by(UserChannel.sequence).all()
        else:
            # 用户未登录，返回默认的频道
            channels = Channel.query.options(load_only(Channel.id, Channel.name)).filter(Channel.is_default == True).all()

        # 序列化
        channel_list = [channel.to_dict() for channel in channels]
        # 插入推荐字段
        channel_list.insert(0, {'id': 0, 'name': '推荐'})
        # 返回数据
        return channel_list

    def put(self):
        """修改用户频道 重置式更新"""
        # 获取请求参数
        userid = g.userid
        channels = request.json.get('channels')

        # 将现有用户关注频道表中的数据全部删除
        UserChannel.query.filter(UserChannel.user_id==userid, UserChannel.is_deleted==False).update({'is_deleted': True})

        # 批量插入
        insert_statement = insert(UserChannel).values([{'user_id': userid, 'channel_id': channel['id'], 'sequence': channel['seq']} for channel in channels])
        # 批量更新
        update_statement = insert_statement.on_duplicate_key_update(is_deleted=False, sequence=insert_statement.inserted.sequence)
        # 执行sql
        db.session.execute(update_statement)
        # 提交事务
        db.session.commit()

        return {'channels': channels}


