import wtforms
from wtforms.validators import Email,Length,EqualTo,InputRequired
from models import UserModel,EmailCaptchaModel
from exts import db,redis
#Form:主要用来验证前端提交的数据是否符合要求，form是一个类，并不用return
class RegisterForm(wtforms.Form):
    email=wtforms.StringField(validators=[Email(message='邮箱格式错误！')])#验证证错误时提示
    captcha=wtforms.StringField(validators=[Length(min=6,max=6,message='验证码格式错误')])
    username=wtforms.StringField(validators=[Length(min=3,max=10,message='用户名不符合规范')])
    password=wtforms.StringField(validators=[Length(min=6,max=20,message='密码格式错误')])
    password_confirm=wtforms.StringField(validators=[EqualTo('password',message='两次输入不一致！')])

    #自定义验证：
    #1。邮箱是否已经被验证
    #2。验证码是否正确
    def validate_email(self,field):
        email=field.data
        user=UserModel.query.filter_by(email=email).first()
        if user:
            raise wtforms.ValidationError(message='该邮箱已经被注册！')

    def validate_captcha(self,field):
        captcha=field.data
        email=self.email.data
        redis_captcha = redis.get(email)
        if redis_captcha is None:
            raise wtforms.ValidationError('验证码已过期或不存在')
        redis_captcha = redis_captcha.decode('utf-8')
        print(captcha, redis_captcha)
        if captcha != redis_captcha:
            raise wtforms.ValidationError('验证码错误')


        #captcha_model=EmailCaptchaModel.query.filter_by(email=email,captcha=captcha).first()
        #if not captcha_model:
        #    raise wtforms.ValidationError(message='邮箱或者验证码错误')

        #可以删掉captcha_model

        # else:
        #     db.session.delete(captcha_model)
        #     db.session.commit()


class LoginForm(wtforms.Form):
    email=wtforms.StringField(validators=[Email(message='邮箱格式错误！')])#验证证错误时提示
    password=wtforms.StringField(validators=[Length(min=6,max=20,message='密码格式错误')])


class QuestionForm(wtforms.Form):
    title=wtforms.StringField(validators=[Length(min=3,max=100,message='标题格式错误')])
    content=wtforms.StringField(validators=[Length(min=3,message='内容格式错误')])


class AnswerForm(wtforms.Form):
    content=wtforms.StringField(validators=[Length(min=1,message='内容格式错误')])
    question_id=wtforms.IntegerField(validators=[InputRequired(message='必须要传入用户ID！')])