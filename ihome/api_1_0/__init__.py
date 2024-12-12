#在init里定义蓝图
from flask import Blueprint


#创建蓝图对象
api=Blueprint('api_1_0',__name__)

from . import demo
from . import verify_code
from . import passport
from . import profile
from . import houses