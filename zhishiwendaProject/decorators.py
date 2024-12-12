from functools import wraps
from flask import g,redirect,url_for,session
#wraps就是为了保留原函数的信息

#就是一些函数
def login_required(func):
    #保留function的信息
    @wraps(func)
    def inner(*args,**kwargs):
        if g.user:
            return func(*args,**kwargs)
        else:
            return redirect(url_for('auth.login'))
    return inner#返回内部函数inner,当调用被装饰的函数时，实际上是调用inner函数
