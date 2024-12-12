import wtforms
from wtforms.validators import Length,EqualTo,InputRequired
from ihome.models import User
from ihome.exts import redis_store
from flask import current_app
#Form:主要用来验证前端提交的数据是否符合要求，form是一个类，并不用return
class RegisterForm(wtforms.Form):
    mobile=wtforms.StringField(validators=[Length(min=11,max=11,message='手机号码格式错误')])#验证证错误时提示
    image_captcha=wtforms.StringField(validators=[Length(min=4,max=4,message='图片验证码格式错误')])
    sms_captcha=wtforms.StringField(validators=[Length(min=4,max=4,message='短信验证码格式错误')])
    password=wtforms.StringField(validators=[Length(min=6,max=20,message='密码格式错误')])
    password_confirm=wtforms.StringField(validators=[EqualTo('password',message='两次输入不一致！')])

    #自定义验证：
    #2。短信验证码是否正确

    def validate_captcha(self,field):
        captcha=field.data
        mobile=self.mobile.data
        try:
            redis_captcha = redis_store.get('sms_code_%s'%mobile)
        except Exception as e:
            current_app.logger.error(e)
        else:
            if redis_captcha is None:
                raise wtforms.ValidationError('验证码已过期或不存在')
            if send_flag is not None:
                # 表示在60秒内之前有过发送的记录
                return jsonify(errno=RET.REQERR, errmsg='请求过于频繁，请60秒后重新操作')
        redis_captcha = redis_store.get('sms_code_%s'%mobile)

        redis_captcha = redis_captcha.decode('utf-8')
        print(captcha, redis_captcha)
        if captcha != redis_captcha:
            raise wtforms.ValidationError('验证码错误')

