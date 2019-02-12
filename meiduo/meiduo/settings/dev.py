"""  开发环境的配置Django settings for meiduo project.Generated by 'django-admin startproject' using Django 1.11.11.For more information on this file, seehttps://docs.djangoproject.com/en/1.11/topics/settings/For the full list of settings and their values, seehttps://docs.djangoproject.com/en/1.11/ref/settings/"""import datetimeimport os, sys# Build paths inside the project like this: os.path.join(BASE_DIR, ...)BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))  # 追加导包路径# print(BASE_DIR)# print(sys.path)# /Users/chao/Desktop/meiduo_sz22/meiduo/meiduo# ['/Users/chao/Desktop/meiduo_sz22/meiduo', '/Users/chao/Desktop/meiduo_sz22', '/Users/chao/.virtualenvs/meiduo/lib/python36.zip', '/Users/chao/.virtualenvs/meiduo/lib/python3.6', '/Users/chao/.virtualenvs/meiduo/lib/python3.6/lib-dynload', '/usr/local/Cellar/python3/3.6.2/Frameworks/Python.framework/Versions/3.6/lib/python3.6', '/Users/chao/.virtualenvs/meiduo/lib/python3.6/site-packages', '/Applications/PyCharm.app/Contents/helpers/pycharm_matplotlib_backend']# Quick-start development settings - unsuitable for production# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/# SECURITY WARNING: keep the secret key used in production secret!SECRET_KEY = 'ne+)ggd(=*se(n84$)j65*=4rkt1(9k@w*vz52*w&js8shvkf)'# SECURITY WARNING: don't run with debug turned on in production!DEBUG = True# 允许那些域名来访问djangoALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'www.meiduo.site', 'api.meiduo.site']# Application definitionINSTALLED_APPS = [    'django.contrib.admin',    'django.contrib.auth',    'django.contrib.contenttypes',    'django.contrib.sessions',    'django.contrib.messages',    'django.contrib.staticfiles',    'rest_framework',  # DRF    'corsheaders', # cors    'ckeditor',  # 富文本编辑器    'ckeditor_uploader',  # 富文本编辑器上传图片模块    'django_crontab',  # 定义时器    'users.apps.UsersConfig',  # 注册用户的子应用    'oauth.apps.OauthConfig',  # QQ    'areas.apps.AreasConfig',  # 省市区    'goods.apps.GoodsConfig',  # 商品    'contents.apps.ContentsConfig',  # 广告]MIDDLEWARE = [    'corsheaders.middleware.CorsMiddleware',  # 最外层的中间件    'django.middleware.security.SecurityMiddleware',    'django.contrib.sessions.middleware.SessionMiddleware',    'django.middleware.common.CommonMiddleware',    'django.middleware.csrf.CsrfViewMiddleware',    'django.contrib.auth.middleware.AuthenticationMiddleware',    'django.contrib.messages.middleware.MessageMiddleware',    'django.middleware.clickjacking.XFrameOptionsMiddleware',]ROOT_URLCONF = 'meiduo.urls'# 模板文件配置项TEMPLATES = [    {        'BACKEND': 'django.template.backends.django.DjangoTemplates',        'DIRS': [os.path.join(BASE_DIR, 'templates')],        'APP_DIRS': True,        'OPTIONS': {            'context_processors': [                'django.template.context_processors.debug',                'django.template.context_processors.request',                'django.contrib.auth.context_processors.auth',                'django.contrib.messages.context_processors.messages',            ],        },    },]WSGI_APPLICATION = 'meiduo.wsgi.application'# Database# https://docs.djangoproject.com/en/1.11/ref/settings/#databasesDATABASES = {    'default': {        'ENGINE': 'django.db.backends.mysql',        'HOST': '192.168.103.210',  # 数据库主机        'PORT': 3306,  # 数据库端口        'USER': 'meiduo_22',  # 数据库用户名        'PASSWORD': 'meiduo_22',  # 数据库用户密码        'NAME': 'meiduo_mall_sz22'  # 数据库名字    }}# Password validation# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validatorsAUTH_PASSWORD_VALIDATORS = [    {        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',    },    {        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',    },    {        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',    },    {        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',    },]# Internationalization# https://docs.djangoproject.com/en/1.11/topics/i18n/# LANGUAGE_CODE = 'en-us'LANGUAGE_CODE = 'zh-hans'# TIME_ZONE = 'UTC'TIME_ZONE = 'Asia/Shanghai'USE_I18N = TrueUSE_L10N = TrueUSE_TZ = True# Static files (CSS, JavaScript, Images)# https://docs.djangoproject.com/en/1.11/howto/static-files/STATIC_URL = '/static/'# 配置redis数据库作为缓存后端CACHES = {    "default": {        "BACKEND": "django_redis.cache.RedisCache",        "LOCATION": "redis://192.168.103.210:6379/0",        "OPTIONS": {            "CLIENT_CLASS": "django_redis.client.DefaultClient",        }    },    "session": {        "BACKEND": "django_redis.cache.RedisCache",        "LOCATION": "redis://192.168.103.210:6379/1",        "OPTIONS": {            "CLIENT_CLASS": "django_redis.client.DefaultClient",        }    },    "verify_codes": {  # 存储短信码        "BACKEND": "django_redis.cache.RedisCache",        "LOCATION": "redis://192.168.103.210:6379/2",        "OPTIONS": {            "CLIENT_CLASS": "django_redis.client.DefaultClient",        }    },    "history": {  # 存储浏览记录        "BACKEND": "django_redis.cache.RedisCache",        "LOCATION": "redis://192.168.103.210:6379/3",        "OPTIONS": {            "CLIENT_CLASS": "django_redis.client.DefaultClient",        }    },    "cart": {  # 存储浏览记录        "BACKEND": "django_redis.cache.RedisCache",        "LOCATION": "redis://192.168.103.210:6379/4",        "OPTIONS": {            "CLIENT_CLASS": "django_redis.client.DefaultClient",        }    },}SESSION_ENGINE = "django.contrib.sessions.backends.cache"SESSION_CACHE_ALIAS = "session"# 日志LOGGING = {    'version': 1,    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器    'formatters': {  # 日志信息显示的格式        'verbose': {            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'        },        'simple': {            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'        },    },    'filters': {  # 对日志进行过滤        'require_debug_true': {  # django在debug模式下才输出日志            '()': 'django.utils.log.RequireDebugTrue',        },    },    'handlers': {  # 日志处理方法        'console': {  # 向终端中输出日志            'level': 'INFO',            'filters': ['require_debug_true'],            'class': 'logging.StreamHandler',            'formatter': 'simple'        },        'file': {  # 向文件中输出日志            'level': 'INFO',            'class': 'logging.handlers.RotatingFileHandler',            'filename': os.path.join(os.path.dirname(BASE_DIR), "logs/meiduo.log"),  # 日志文件的位置            'maxBytes': 300 * 1024 * 1024,            'backupCount': 10,            'formatter': 'verbose'        },    },    'loggers': {  # 日志器        'django': {  # 定义了一个名为django的日志器            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志            'propagate': True,  # 是否继续传递日志信息            'level': 'INFO',  # 日志器接收的最低日志级别        },    }}# DRF配置项REST_FRAMEWORK = {    # 自定义异常捕获    'EXCEPTION_HANDLER': 'meiduo.utils.exceptions.exception_handler',    'DEFAULT_AUTHENTICATION_CLASSES': (  # 配置全局认证类(验证登录用户是不是本网站用户)        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',  # JWT认证(默认认证方案)        'rest_framework.authentication.SessionAuthentication',  # session认证        'rest_framework.authentication.BasicAuthentication',  # 基础认证    ),    # 全局分页    'DEFAULT_PAGINATION_CLASS': 'meiduo.utils.paginations.StandardResultsSetPagination',}# 修改用户模型类  String model references must be of the form 'app_label.ModelName'# 修改用户模型类的导包路径必须 是  应用名.模型名 这种格式AUTH_USER_MODEL = 'users.User'# CORS  追加白名单CORS_ORIGIN_WHITELIST = (    '127.0.0.1:8080',    'localhost:8080',    'www.meiduo.site:8080',    'api.meiduo.site:8000')CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie# JWT配置项JWT_AUTH = {    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),  # 指定JWT token有效期    # 修改jwt登录后响应体函数    'JWT_RESPONSE_PAYLOAD_HANDLER': 'users.utils.jwt_response_payload_handler'}# 修改默认的认证后端AUTHENTICATION_BACKENDS = [    'users.utils.UsernameMobileAuthBackend',  # 修改django认证后端类]# QQ登录参数配置QQ_CLIENT_ID = '101514053'QQ_CLIENT_SECRET = '1075e75648566262ea35afa688073012'QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'EMAIL_PORT = 25EMAIL_HOST = 'smtp.163.com'#发送邮件的邮箱EMAIL_HOST_USER = 'itcast99@163.com'#在邮箱中设置的客户端授权密码EMAIL_HOST_PASSWORD = 'python99'#收件人看到的发件人EMAIL_FROM = 'python<itcast99@163.com>'# DRF扩展REST_FRAMEWORK_EXTENSIONS = {    # 缓存时间    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 60,    # 缓存存储    'DEFAULT_USE_CACHE': 'default',}# FastDFSFDFS_BASE_URL = 'http://192.168.103.210:8888/'FDFS_CLIENT_CONF = os.path.join(BASE_DIR, 'utils/fastdfs/client.conf')# django文件存储DEFAULT_FILE_STORAGE = 'meiduo.utils.fastdfs.fdfs_storage.FastDFSStorage'# 富文本编辑器ckeditor配置CKEDITOR_CONFIGS = {    'default': {        'toolbar': 'full',  # 工具条功能        'height': 300,  # 编辑器高度        # 'width': 300,  # 编辑器宽    },}CKEDITOR_UPLOAD_PATH = ''  # 上传图片保存路径，使用了FastDFS，所以此处设为''# 生成的静态html文件保存目录GENERATED_STATIC_HTML_FILES_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'front_end_pc')CRONJOBS = [    # 每5分钟执行一次生成主页静态文件    ('*/1 * * * *', 'contents.crons.generate_static_index_html', '>> /Users/chao/Desktop/meiduo_sz22/meiduo/logs/crontab.log')]# 解决crontab中文问题CRONTAB_COMMAND_PREFIX = 'LANG_ALL=zh_cn.UTF-8'