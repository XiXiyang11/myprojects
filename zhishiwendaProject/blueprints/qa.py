from flask import Blueprint, render_template, request, g, redirect, url_for, jsonify
from .forms import QuestionForm,AnswerForm
from models import QuestionModel,AnswerModel,UserModel
from exts import db,redis,socketio
from decorators import login_required
from flask_socketio import SocketIO,send,emit
bp=Blueprint('qa',__name__,url_prefix='/')
@bp.route('/')
def index():
    questions=QuestionModel.query.order_by(QuestionModel.create_time.desc()).all()

    return render_template('index.html',questions=questions)

@bp.route('/qa/publish',methods=['GET','POST'])
@login_required
def publish():
    # if not g.user:
    #     return redirect(url_for('auth.login'))#但这样的话，如果有十个页面都要求登录之后才能访问，这样的放就要复制这两句话十次，会产生代码冗余，所以要用到装饰器这个东西
    if request.method=='GET':
        return render_template('public_question.html')
    else:
        form=QuestionForm(request.form)
        if form.validate():
            title=form.title.data
            content =form.content.data
            question=QuestionModel(title=title,content=content,author=g.user)#g是一个全局变量，里边放的是userid
            db.session.add(question)
            db.session.commit()
            #跳转到帖子的详情页
            return redirect('/')
        else:
            print(form.errors)
            return redirect(url_for('question'))


@bp.route('/qa/detail/<qa_id>')
def qa_detail(qa_id):
    question=QuestionModel.query.get(qa_id)
    return render_template('detail.html',question=question)
    #question=question是为了让这个参数再传回模板当中


@bp.route('/qa/set', methods=['GET','POST'])
def redisset():
    if request.method=='GET':
        return render_template('redistest.html')
    else:
        # 获取请求参数
        key = request.form.get('key')
        value = request.form.get('value')
        # 存储数据到redis
        redis.set(key, value)
        # 返回响应
        return jsonify({'message': 'Data saved successfully'})


@bp.route('/answer/publish',methods=['POST'])
@login_required#调用这个装饰器，只有登录之后才可以评论

#1。验证表单信息是否正确
#2。if判断表单信息语句是否正确，如果成功，则添加信息，并且返回这个信息，显示到页面上
#3。如果信息不正确，则打印错误信息，再返回这个问题详情界面且评论的东西清空，并且再返回question_id
def publish_answer():
    form=AnswerForm(request.form)#先看一下传回来的表单信息符不符合规范
    if form.validate():
        content=form.content.data
        question_id=form.question_id.data
        answer=AnswerModel(content=content,question_id=question_id,author_id=g.user.id)
        db.session.add(answer)
        db.session.commit()
        return redirect(url_for('qa.qa_detail',qa_id=question_id))
    else:
        print('answer的格式不符合规范！')
        return redirect(url_for('qa.qa_detail',qa_id=request.form.get('question_id')))

@bp.route('/search')
def search():
    #1.通过查询字符串的形式：/search?q='关键字'
    #2。直接把参数放到路径当中，跟上边的qa_detail一样，/search/<q>
    #3.使用post方法，reqest.form,现在使用第一种方法
    q=request.args.get('q')
    questions=QuestionModel.query.filter(QuestionModel.title.contains(q)).all()
    return render_template('index.html',questions=questions)

@bp.route('/mypublish')
@login_required#调用这个装饰器，只有登录之后才可以评论
def mypublish():
    questions=QuestionModel.query.filter_by(author_id=g.user.id).order_by(QuestionModel.create_time.desc()).all()
    return render_template('index.html',questions=questions)
#<flask全栈开发>，前端，后端，怎么部署到阿里去服务器，怎么上传图片，文件
#《flask实战》，flask+vue前后端分享的论坛系统，webSocket实战（实现未读消息的显示）

@bp.route('/onlinechat')
@login_required
def onlinechat():

    return render_template('chat.html')
@socketio.on('message')#这个装饰器用于处理客户端发送的消息
def handle_meessage(data):
    user_id = data['user_id']
    message = data['message']
    user = UserModel.query.get(user_id)
    if user:
        user_name = user.username
        print(f'Message from {user_name}: {message}')
        # 广播消息到所有连接的客户端
        socketio.emit('message', {'user_name': user_name, 'message': message})
    else:
        print(f'Unknown user ID: {user_id}')