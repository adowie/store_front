import os

"""
dev configs
"""
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True
SQLALCHEMY_ECHO = False
MAIL_SERVER = "smtp.googlemail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = "admin@ourstorefront.online"
MAIL_PASSWORD = os.getenv('SMTP_MAIL_PASS')
ADMINS = ["adowie01@gmail.com","admin@ourstorefront.online"]

SECRET_KEY = os.getenv('FLASK_SECKRET_KEY')
POSTS_PER_PAGE = 6
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')
SEND_EMAIL = True

PRODUCT_IMAGES_DIR = 'app/static/img/products/'
PRODUCT_CATEGORY_IMAGES_DIR = 'app/static/img/products/categories/'
COMPANY_IMAGES_DIR =  'app/static/img/company/'
CUSTOMER_IMAGES_DIR =  'app/static/img/customers/'
USER_IMAGES_DIR = 'app/static/img/user/'

# basedir = os.path.abspath(os.path.dirname(__file__))
DB_PASS = os.getenv('DB_PASS')
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://adowie01:"+DB_PASS+"@adowie01.mysql.pythonanywhere-services.com/adowie01$osfo"
# # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
# SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_mysql_repository')
# SQLALCHEMY_TRACK_MODIFICATIONS = True

