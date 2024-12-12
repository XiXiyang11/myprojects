'''这个蓝图就是用来保存静态文件的'''
from flask import Blueprint,current_app,make_response
#make_response可以创建一个返回响应的对象，在这个对象中可以添加cookie
from flask_wtf import csrf
#提供静态文件的蓝图
html=Blueprint('web_html',__name__)

#127。0。0。1：5000/()
#127.0.0.1:5000/(register.html)
#127.0.0.1:5000/favicon.ico #浏览器认为的网站标识
@html.route("/<re(r'.*'):html_file_name>")
def get_html(html_file_name):
    '''提供html文件'''
    #如果htmlfilename为空，表示 访问的路径是/,请求的是主页
    if not html_file_name:
        html_file_name='index.html'
    #如果资源名不是favicon.ico,就不用加html/，favicon直接放在了static文件夹下
    if html_file_name!='favicon.ico':
        html_file_name='html/'+html_file_name

    #创建一个csrf_token值
    csrf_token=csrf.generate_csrf()
    #flask提供的返回静态文件的方法
    resp=make_response(current_app.send_static_file(html_file_name))
    #设置cookie值
    resp.set_cookie('csrf_token',csrf_token)

    return resp