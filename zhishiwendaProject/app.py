from flask import Flask,session,g#session会话管理功能，可存储数据，g是一个全局变量，只在一次请求中会保存
from flask_migrate import Migrate#提供数据库迁移功能

import config
from exts import db,mail,redis,socketio#db是一个sqlalchmey对象

from blueprints.qa import bp as qa_bp#导入蓝图，在这个.py文件里已经导入了Blueprint，创建了blueprint对象了已经
from blueprints.auth import bp as auth_bp#导入蓝图
from models import UserModel
app = Flask(__name__)
#绑定配置文件，会自动加载配置信息
app.config.from_object(config)#使用它加载配置类
db.init_app(app)#将app与db对象绑定，
mail.init_app(app)
socketio.init_app(app)
migrate=Migrate(app,db)#使得migrate将app和db结合
redis.init_app(app)
app.register_blueprint(qa_bp)#注册蓝图
app.register_blueprint(auth_bp)#注册蓝图
@app.route('/')
def hello_world():
    return 'Hello World!'



#下边的两个钩子函数主要是为了在导航栏那登录之后显示出用户名，在上下文处理器那里放，而不是在每个界面都重新渲染一回
@app.before_request
def my_before_request():
    user_id=session.get('user_id')
    if user_id:
        user=UserModel.query.get(user_id)
        setattr(g,'user',user)#g:global，g这个变量在一次请求完毕之后，它的值就没有了，所有在每次发送请求时都用这个钩子函数来给g它重新赋值
    else:
        setattr(g,'user',None)


#上下文处理器，渲染之后，一次性就可以让所有的页面得到这个user对象
@app.context_processor#每当渲染模板时，都会调用这个被装饰的函数，并将返回的字典中的键值对添加到模板上下文中
#渲染模板的意思是将模板文件与数据结合起来，生成最终的html内容的过程。可通过定义模板文件并在视图函数中传递数据，可以生成动态的网页内容。
def my_context_processor():

    return{'user':g.user}

if __name__ == '__main__':
    app.run(threaded=True)
