from exts import db
from datetime import datetime


#models里边都是数据库表的实体，即ORM模型，在这里定义数据库中的字段
class UserModel(db.Model):
    __tablename__='user'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String(100),nullable=False)
    password=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(100),nullable=False,unique=True)
    join_time=db.Column(db.DateTime,default=datetime.now)

class EmailCaptchaModel(db.Model):
    __tablename__='email_captcha'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)

    email=db.Column(db.String(100),nullable=False,unique=True)
    captcha=db.Column(db.String(100),nullable=False)


class QuestionModel(db.Model):
    __tablename__='question'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    title=db.Column(db.String(100),nullable=False)
    content=db.Column(db.Text,nullable=False)
    create_time=db.Column(db.DateTime,default=datetime.now)


    #需要用户的一个外键
    author_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    #反向引用，为了根据用户id找到用户发布过的所有问答
    author=db.relationship(UserModel,backref='questions')
    #上行代码有两个意思，1：questionmodel中有一个可指向usermodel实例的指针，通过.author就可以访问到对应的user对象
    #2：backref=questions表示 在usermodel实例中创建了一个questions属性，user通过这个属性可以返回这个user提问的所有问题，user.questions

class AnswerModel(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)

    #添加两个外键，一个是评价的作者id,一个是评论的帖子id
    question_id=db.Column(db.Integer,db.ForeignKey('question.id'))
    author_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    #还需要定义两个关系
    questioin=db.relationship(QuestionModel,backref=db.backref('answers',order_by=create_time.desc()))
    author=db.relationship(UserModel,backref='answers')