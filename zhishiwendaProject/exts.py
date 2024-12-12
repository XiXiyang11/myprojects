#加载flask-sqlalchemy
from flask_sqlalchemy import SQLAlchemy#一个第三方库，提供SQLAlchemy ORM的集成，方便操作数据库
from flask_mail import Mail#提供电子邮件发送功能
from flask_redis import FlaskRedis#提供redis数据库的使用
from flask_socketio import SocketIO#提供实时通信功能

socketio = SocketIO()
db=SQLAlchemy()#创建一个空的db对象，在app里再引入db
mail=Mail()
redis=FlaskRedis()