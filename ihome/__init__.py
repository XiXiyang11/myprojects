from flask import Flask
from config import config_map#导入配置文件
from ihome.exts import db,session,csrfprotect,redis_store
import logging#使用的python的日志文件
from logging.handlers import RotatingFileHandler
from ihome import api_1_0
from ihome.utils.commons import ReConverter
from ihome.libs.yuntongxun.SmsSDK import SmsSDK
#要把项目做成工厂模式，就是分清楚app的运行环境，在开发环境下就执行开发环境的配置，在真正运行app的环境下就执行生产环境配置信息
#所以需要定义一个函数来区分一下



#设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)#调试debug级
#创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler=RotatingFileHandler('logs/log',maxBytes=1024*1024*100,backupCount=10)
#创建日志记录的格式
formatter=logging.Formatter('%(levelname)s  %(filename)s:%(lineno)d %(message)s')
#为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
#为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)


def create_app(Config):
    """
    用来创建flask应用对象
    :param Config: 配置模式的名称，（’develop‘,'product'）
    :return: 返回app对象
    """
    app = Flask(__name__)
    config_class=config_map.get(Config)#根据配置模式的名字获取配置参数的类
    app.config.from_object(config_class)  # 将app绑定配置文件
    db.init_app(app)
    redis_store.init_app(app)
    session.init_app(app)  # 要把session数据保存到redis数据库中，就是修改了默认配置，不再保护在cookie中
    csrfprotect.init_app(app)  # 为flask补充csrf防护

    '''global redis_store
    redis_store=redis.StrictRedis(host=config_class.REDIS_HOST,
                                  port=config_class.REDIS_PORT,
                                  password=config_class.REDIS_PASSWORD)
    try:
        # 尝试发送一个 PING 命令来测试连接
        response = redis_store.ping()
        if response:
            print({"status": "success", "message": "Connected to Redis!"})
        else:
            print({"status": "failure", "message": "Failed to ping Redis."})
    except redis.exceptions.ConnectionError as e:
        print({"status": "failure", "message": f"Failed to connect to Redis: {str(e)}"})'''
    #为flask添加自定义转换器
    app.url_map.converters['re']=ReConverter

    #注册蓝图
    app.register_blueprint(api_1_0.api,url_prefix='/api/v1.0')
    #注册提供静态文件的蓝图
    from ihome import web_html
    app.register_blueprint(web_html.html)
    return app