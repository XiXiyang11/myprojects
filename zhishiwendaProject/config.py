
SECRET_KEY='asdfewjrgenw'#设置的密钥，用于对会话数据进行签名
#配置数据库--mysql数据库
hostname='127.0.0.1'
port='3306'
database='zhishiwenda'
username='root'
password='yxy123'
db_url='mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(username,password,hostname,port,database)
SQLALCHEMY_DATABASE_URI=db_url

#配置redis数据库
REDIS_URL = "redis://:yxy123@127.0.0.1:6379/0"#最后的0应该指的是0号数据库
#配置邮箱

MAIL_SERVER='smtp.163.com'
MAIL_USE_SSL=True
MAIL_PORT=465
MAIL_USERNAME='yxy15532066085@163.com'
MAIL_PASSWORD='WSTV3MBdVVNqjX4z'
MAIL_DEFAULT_SENDER='yxy15532066085@163.com'