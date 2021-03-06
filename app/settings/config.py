class DefaultConfig:
    """默认配置"""

    # mysql配置
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:mysql@127.0.0.1:3306/toutiao"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁止追踪
    SQLALCHEMY_ECHO = False  # 禁止输出sql语句

    # redis配置
    REDIS_LOCATION = "127.0.0.1"
    REDIS_PORT = 6381

    # jwt过期时间
    JWT_EXPIRE_DAYS = 14
    JWT_SECRET = "gciLfSjy5pc5/1iusAC2ZiygkyI="



config_dict = {
    "dev": DefaultConfig
}
