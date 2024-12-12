
from flask import Blueprint, render_template, jsonify, redirect, url_for, session, flash,current_app
#Blueprint导入
from exts import mail,db,redis
from flask_mail import Message
from flask import request#是一个全局变量，用于返回当前请求的对象，session也是一个全局变量，用于返回当前的会话对象
import string#为了产生随机的验证码
import random
import hashlib
import threading
from datetime import datetime
from models import EmailCaptchaModel,UserModel
from .forms import RegisterForm,LoginForm
bp=Blueprint('auth',__name__,url_prefix='/auth')#prefix:url前缀，创建blueprint对象
# 生成 MD5 哈希值
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()



@bp.route('/login',methods=['GET','POST'])#这个地址是/auth/login
def login():
    if request.method=='GET':
         return render_template('login.html')
    else:
        form =LoginForm(request.form)#把前端提交上来的表单先放入form规则里，验证一下前端返加的数据是否符合规范，再返回一个相同的表单
        if form.validate():#validate()是自带的一个属性，判断所有的数据是不是都符合规范
            email=form.email.data
            password = form.password.data
            user=UserModel.query.filter_by(email=email).first()
            if not user:
                print('邮箱在数据库中不存在！')
                return redirect(url_for('auth.login'))
            if user and user.password == hash_password(password):
                print('登录成功')
                #cookie中不适合存储太多的数据，只适合存储少量的数据
                #cookie一般用来存放登录授权的东西
                #flask中的session,是经过加密后存储在cookie中的
                session['user_id']=user.id#session会加密，然后放到cookies当中，传给浏览器
                return redirect('/')
            else:
                print('密码错误！')
                return redirect(url_for('auth.login'))
        else:
            print(form.errors)
            return redirect(url_for('auth.login'))
#get:从服务器上获取数据
#post:将客户端的数据提交给服务器，rout默认是get请求
@bp.route('register',methods=['GET','POST'])#注册
def register():
    form = RegisterForm(request.form)
    if request.method == 'GET':
        #要做表单验证，flask-wtf:wtforms可做
        return render_template('register.html',form=form)
    else:

        if form.validate():
            email=form.email.data
            username=form.username.data
            password=form.password.data
            # 生成密码的 MD5 哈希值
            password_hash = hash_password(password)
            user=UserModel(email=email,username=username,password=password_hash)#可以通过md5进行哈希加密，然后再放入数据库中，数据库里一般不要放明文密码，很容易被盗取
            db.session.add(user)
            db.session.commit()
            flash('注册成功！')
            return redirect(url_for('auth.login'))
        else:
            print(form.errors)
            flash('注册失败！')
            return render_template('register.html', form=form)

def send_email(app,email,captcha):
    with app.app_context():
        mail = app.extensions.get('mail')  # 获取 Flask-Mail 扩展
        message = Message(subject='园园和小蒙专属论坛注册验证码', recipients=[email],
                          body=f'您的验证码为{captcha},请尽快使用，五分钟后失效')
        mail.send(message)
        print(f"Email sending thread ID: {threading.current_thread().ident}")
        print(f"{datetime.now()}:Verification code sent to {email} with captcha {captcha}")

@bp.route('captcha/email',methods=['GET'])#默认的请求方式是get
def get_email_captcha():
    #先获取注册时用户写的邮箱

    email=request.args.get('email')
    source=string.digits*6
    captcha=random.sample(source,6)
    captcha="".join(captcha)#把字符数组转换成字符串，双引号里填分隔符
    print(datetime.now(),email,captcha)
    redis.set(email,captcha,ex=300)
    try:

        #存储验证码，要学习memchached/redis,但博主现在用的是数据库存取方式
        #email_captcha=EmailCaptchaModel(email=email,captcha=captcha)
        #db.session.add(email_captcha)
        #db.session.commit()
        # 打印当前应用对象的所有属性
        app = current_app._get_current_object()

        thread = threading.Thread(target=send_email, args=(app,email,captcha,))
        thread.start()
        print(f"Email sended thread ID: {threading.current_thread().ident}")
        return jsonify({'code':200,'message':'','data':None})

    except OSError as e:
        return f"Error sending email: {e}"

    return jsonify({'code': 200, 'message': '', 'data': None})


@bp.route('/logout')
def logout():
    #把session中的信息清掉之后就退出登录了
    session.clear()
    return redirect(('/'))