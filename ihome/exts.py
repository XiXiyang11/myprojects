from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_redis import FlaskRedis
from ihome.libs.yuntongxun.SmsSDK import SmsSDK
db=SQLAlchemy()
session=Session()
csrfprotect=CSRFProtect()#为了给表单数据添加防护机制，加密，少受攻击
redis_store=FlaskRedis()
sdk = SmsSDK(accId='2c94811c936de29c019376948b4b0199',
                 accToken='1d9a25a12ea54e13a23b7c65b609b478',
                 appId='2c94811c936de29c019376948ced01a0')