from ihome import create_app
from ihome.exts import db
from flask_migrate import Migrate
import os
#创建flask的应用对象
app=create_app('develop')
Migrate(app,db)#从flask2.0版本开始，就可以在终端使用flask db命令了，不用再手支导入MigrateCoomand

if __name__ == '__main__':

    app.run()
