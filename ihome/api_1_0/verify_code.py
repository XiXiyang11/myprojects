

from . import api
from ihome.utils.captcha.captcha import captcha
from ihome.utils.response_code import RET
from ihome.exts import redis_store,db,sdk
from ihome import constants
from flask import current_app,jsonify,make_response,request
from ihome.models import User
import random
import json
#GET 127.0.0.1/api/v1.0/image_codes/<image_code_id>
@api.route('/image_codes/<image_code_id>')
def get_image_code(image_code_id):
    '''获取图片验证码，接口名不带动词，应该用get方式访问这个视图
    前端传的时候，传一个image_code_id,这个值默认是不能为空的
    正常：返回验证码图片  异常：抛出json数据
    '''
    #获取参数，检验参数都有了，因为这个视图变量是必须传的，如果不传是进不来这个视图函数的
    #业务逻辑处理
    #生成验证码图片，将验证码真实值与编号保存到redis中

    #生成验证码图片,返回名字，真实文本，图片数据
    name,text,image_data=captcha.generate_captcha()

    '''try:
        # 尝试发送一个 PING 命令来测试连接
        response = redis_store.ping()
        if response:
            print('verify_code_test:',{"status": "success", "message": "Connected to Redis!"})
        else:
            print('verify_code_test:',{"status": "failure", "message": "Failed to ping Redis."})
    except redis.exceptions.ConnectionError as e:
        print('verify_code_test:',{"status": "failure", "message": f"Failed to connect to Redis: {str(e)}"})'''
    #将验证码真实值与编号保存到redis中，设置有效期
    # redis里的存放value数据类型有，字符串，列表，哈希，set
    # redis_store.set('image_code%s'%image_code_id,text)
    # redis_store.expire('image_code%s'%image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES)
    #                    key                           有效期                           value
    try:
        redis_store.setex('image_code_%s'%image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
    except Exception as e:
        #捕获异常，记录日志
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='redis save image code id failed')
    #返回图片
    print('注册时的图片验证码：',text,'图片id',image_code_id)
    resp=make_response(image_data)
    resp.headers['Content-Type']='image/jpg'
    return resp


#GET /api/v1.0/sms_codes/<telephone>/?image_code=xxx&image_code_id=xxx
#最后是为了验证一下，图片验证码是否正确
@api.route('/sms_codes/<re(r"1[34578]\d{9}"):telephone>')
def get_sms_code(telephone):
    '''获取短信验证码'''
    #获取参数，校验参数，业务逻辑处理，返回值
    #获取参数
    image_code=request.args.get('image_code')
    image_code_id=request.args.get('image_code_id')

    #校验参数
    if not all([image_code,image_code_id]):
        #表示参数不完整
        return jsonify(errno=RET.PARAMERR,errmsg='图片验证码参数不完整')

    #业务逻辑处理
    #从redis中取出真实的图片验证码
    try:
        #判断数据库获取数据是否异常
        real_image_code=redis_store.get('image_code_%s'%image_code_id).decode('utf-8')
        print(image_code,real_image_code,telephone)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='redis数据库异常')
    #判断图片验证码是否过期：
    if real_image_code is None:
        #因为设置了图片验证码的有效期，所以可能会是none,所以看看是不是none
        return jsonify(errno=RET.NODATA,errmsg='图片验证码失效')
    #删除redis中的图片验证码，防止用户使用同一个图片验证码验证多次
    try:
        redis_store.delete('image_code_%s'%image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    # 与用户填写的值进行对比
    if real_image_code!=image_code:
        #表示用户填写错误
        return jsonify(errno=RET.DATAERR,errmsg='图片验证码错误')
    #判断对于这个手机号的操作，在60秒内有没有之前的记录，如果有，则认为用户操作频繁，不接受处理
    try:
        send_flag=redis_store.get('send_sms_code_%s' % telephone)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            #表示在60秒内之前有过发送的记录
            return jsonify(errno=RET.REQERR,errmsg='请求过于频繁，请60秒后重新操作')
    #判断手机号是否已经注册
    try:
        user=User.query.filter_by(mobile=telephone).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            #表示手机号已存在

            return jsonify(errno=RET.DATAEXIST,errmsg='手机号已存在')
    #如果手机号不存在，则生成短信验证码
    sms_code='%04d'%random.randint(0,9999)


    #保存真实的短信验证码到redis数据库中
    try:
        redis_store.setex('sms_code_%s'%telephone,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        #保存发送给这个手机号的记录，防止用户在60s内再次出发发送短信的操作
        redis_store.setex('send_sms_code_%s' % telephone,constants.SEND_SMS_CODE_INTERVAL,1)
        print('短信验证码：',sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='保存短信验证码异常')
    #发送短信
    try:
        ret = sdk.sendMessage(1, telephone, (sms_code, int(constants.SMS_CODE_REDIS_EXPIRES/60)))
    except Exception as e:
        current_app.logger.error(e)
    result=json.loads(ret)
    if result['statusCode']!='000000':
        #发送失败
        return jsonify(errno=RET.THIRDERR,errmsg='发送失败')
    else:
        return jsonify(errno=RET.OK,errmsg='发送成功')
