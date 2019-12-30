from flask_restful import Resource
from sqlalchemy.orm import load_only

from models.article import Channel


class ChannelResource(Resource):
    """获取所有频道"""
    def get(self):
        channels = Channel.query.options(load_only(Channel.id, Channel.name)).all()
        # 序列化
        channel_list = [{"id": channel.id, "name": channel.name} for channel in channels]
        # 返回数据
        return {"channels": channel_list}
