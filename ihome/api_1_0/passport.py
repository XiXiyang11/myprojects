from . import api #导入这个蓝图
from flask import request,jsonify,current_app,session
from ihome.utils.response_code import RET
import re
from ihome.exts import redis_store,db
from ihome.models import User
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash,check_password_hash

#POST /api/v1.0/users
from .. import constants


@api.route('/users',methods=['POST'])
def register():
    '''用户注册
    请求的参数：手机号、短信验证码、密码
    传入的参数格式：json
    '''
    req_dict=request.get_json()
    mobile=req_dict.get('mobile')
    sms_code=req_dict.get('sms_code')
    password=req_dict.get('password')
    password2=req_dict.get('password2')

    #校验参数
    if not all([mobile,sms_code,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')

    #判断手机号格式
    if not re.match(r'1[34578]\d{9}',mobile):
        #表示格式不对
        return jsonify(errno=RET.PARAMERR,errmsg='手机号格式错误')
    if password!=password2:
        return jsonify(errno=RET.PARAMERR,errmsg='两次密码不一致')
    #从redis中取出短信验证码
    #判断短信验证码是否过期
    #判断用户填写的短信验证码的正确性
    try:
        redis_captcha = redis_store.get('sms_code_%s' % mobile).decode('utf-8')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='读取真实短信验证码异常')
    else:
        if redis_captcha is None:
            return jsonify(errno=RET.DATAEXIST,errmsg='短信验证码已失效')
    #删除redis中的短信验证码，防止重复使用校验
    try:
        redis_store.delete('sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
    print('发送的短信验证码和用户输入的验证码：',redis_captcha,sms_code)
    if redis_captcha != sms_code:
        return jsonify(errno=RET.DATAERR,errmsg='短信验证码错误')
    # 判断手机号是否已经注册

    user = User(name=mobile, mobile=mobile, password=password)
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()#事务的回滚
        #表示手机号出现了重复值，即手机号已经被注册过了
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST,errmsg='手机号已存在')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='数据库异常')
    #保存登录状态到session中
    session['name']=mobile
    session['mobile']=mobile
    session['user_id']=user.id

    return jsonify(errno=RET.OK, errmsg='用户注册成功')

@api.route("/sessions", methods=["POST"])
def login():
    """用户登录
    参数： 手机号、密码， json
    """
    # 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    password = req_dict.get("password")

    # 校验参数
    # 参数完整的校验
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 手机号的格式
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    # 判断错误次数是否超过限制，如果超过限制，则返回
    # redis记录： "access_nums_请求的ip": "次数"
    user_ip = request.remote_addr  # 用户的ip地址
    try:
        access_nums = redis_store.get("access_num_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums) >= constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, errmsg="错误次数过多，请稍后重试")

    # 从数据库中根据手机号查询用户的数据对象
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    # 用数据库的密码与用户填写的密码进行对比验证
    if user is None or not user.check_password(password):
        # 如果验证失败，记录错误次数，返回信息
        try:
            # redis的incr可以对字符串类型的数字数据进行加一操作，如果数据一开始不存在，则会初始化为1
            redis_store.incr("access_num_%s" % user_ip)
            redis_store.expire("access_num_%s" % user_ip, constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)

        return jsonify(errno=RET.DATAERR, errmsg="用户名或密码错误")

    # 如果验证相同成功，保存登录状态， 在session中
    session["name"] = user.name
    session["mobile"] = user.mobile
    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg="登录成功")


@api.route("/session", methods=["GET"])
def check_login():
    """检查登陆状态"""
    # 尝试从session中获取用户的名字
    name = session.get("name")
    # 如果session中数据name名字存在，则表示用户已登录，否则未登录
    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="false")


@api.route("/session", methods=["DELETE"])
def logout():
    """登出"""
    # 清除session数据
    session.clear()
    return jsonify(errno=RET.OK, errmsg="OK")