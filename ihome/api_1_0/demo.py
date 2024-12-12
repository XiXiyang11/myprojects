from . import api
from ihome.exts import db
from flask import current_app#导入应用上下文对象
import os
import ihome.models

@api.route('/')
def index():
    # current_app.logger.error('errormsg')
    # current_app.logger.warn('warnmsg')
    # current_app.logger.info('infomsg')
    # current_app.logger.debug('debugmsg')用这种方式可以写入日志

    return f"FLASK_RUN_PORT: {os.getenv('FLASK_RUN_PORT')},PORT: {os.getenv('PORT')}"
