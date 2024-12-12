import redis

class Config(object):
    #这是一个父类，可能在测试时和真正部署时用到的配置是不一样的，所以让子类去继承父类，在不同的运行环境下，设置不一样的参数值吧

    SECRET_KEY = 'DLSAKFJASDFASLFJ'  # SESSION会话对应的加密密码
    # 配置mysql数据库
    USERNAME = 'root'
    HOSTNAME = '127.0.0.1'
    PORT = 3306
    DATABASE = 'aifang'
    PASSWORD = 'yxy123'
    # pymysql是指的数据库驱动
    DB_URL = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
    SQLALCHEMY_DATABASE_URI = DB_URL
    # 配置redis数据库
    REDIS_HOST='127.0.0.1'
    REDIS_PORT=6379
    REDIS_PASSWORD='yxy123'
    REDIS_URL = 'redis://:yxy123@127.0.0.1:6379/1'
    # Flask-Session配置
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host='127.0.0.1', port=6379, password='yxy123')
    SESSION_USE_SIGNER = True  # 对cookie中的sessionid进行隐藏，不在cookie中显示
    PERMANENT_SESSION_LIFETIME = 86400  # SESSION数据的有效期，单位秒

    #短信的配置


class DevelopmentCofig(Config):
    #这是开发模式的配置信息，当debug模式开启时，会强制忽略自己设置的日志信息，也就是什么级别的log信息 都会保存
    DEBUG = True

class ProductConfig(Config):
    """生产环境配置信息"""
    #如果是在生产环境模式下，自己的log设置才会生效，比如想保留哪个级别的数据就保留哪个级别的数据
    pass

config_map={
    'develop':DevelopmentCofig,
    'product':ProductConfig
}