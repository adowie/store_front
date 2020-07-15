from dotenv import load_dotenv
import os
import sys


path = '/home/adowie/osfo_live'
if path not in sys.path:
    sys.path.append(path)

project_folder = os.path.expanduser('~/osfo_live')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

"""
dev configs
"""

DEBUG = True
SQLALCHEMY_ECHO = False
MAIL_SERVER = "smtp.yandex.com"
# MAIL_PORT = 587
MAIL_PORT = 465
MAIL_USE_TLS = True
MAIL_USERNAME = "admin@ourstorefront.online"
# MAIL_USERNAME = "ourstorefrontonline@gmail.com"
MAIL_PASSWORD = "abeezxidbwiwvuvg"#"meoqjgpaighaoqid"#os.getenv('SMTP_MAIL_PASS')
ADMINS = ["admin@ourstorefront.online","error@ourstorefront.online"]


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
DB_HOST = os.getenv('DB_SERVER')
DB_USER = os.getenv('DB_USER')
DB_ = os.getenv('DBASE')

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://"+DB_USER+":"+DB_PASS+"@"+DB_HOST+"/"+DB_
# # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
# SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_mysql_repository')
# SQLALCHEMY_TRACK_MODIFICATIONS = True


