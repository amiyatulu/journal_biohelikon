# Django settings for newproject project.


DEBUG = False
TEMPLATE_DEBUG = DEBUG
PREPEND_WWW = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
ALLOWED_HOSTS = ['.biohelikon.org']
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'biohelik_central',                      # Or path to database file if using sqlite3.
        'USER': 'biohelik_biobio',                      # Not used with sqlite3.
        'PASSWORD': '$3heuieo#@&',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', 
	
	'OPTIONS': {
		"init_command": "SET storage_engine=INNODB",
		}

                     # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.

EMAIL_HOST = 'smtp.webfaction.com'
EMAIL_HOST_USER = 'biohelikon'
EMAIL_HOST_PASSWORD = 'p#ct$p&'
DEFAULT_FROM_EMAIL = 'Biohelikon <contact@biohelikon.org>'

TIME_ZONE = 'UTC'
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/home/amiyatulu/webapps/staticbiohelik/djangocentralmediafiles/'
HIDDEN_ROOT = '/home/amiyatulu/webapps/biohelik/djangocentral/files/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = 'http://biohelikon.org/static/djangocentralmediafiles/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = "/home/amiyatulu/webapps/staticbiohelik/djangocentralstaticfiles/"

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "http://biohelikon.org/static/djangocentralstaticfiles/"

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = 'http://biohelikon.org/djangocentralstaticfiles/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    "/home/amiyatulu/webapps/biohelik/djangocentral/static",
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '36y+9(j_iqllfwa3!z*yny^n6k!@@c7k5%b^5q%2*w^75y(v0'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'central.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/home/amiyatulu/webapps/biohelik/djangocentral/django_templates",
)
RECAPTCHA_PUBLIC_KEY = '6LfsbQkTAAAAABGXK3a86JLkodCeMgfr052u0VpW'
RECAPTCHA_PRIVATE_KEY = '6LfsbQkTAAAAADDlPY-ssxF1Dlva0-9wrIL1OG6X'
NOCAPTCHA = True
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'tracking',
    'journal',
    'mailing',
    'haystack',
    'captcha',
)
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
}

TEMPLATE_CONTEXT_PROCESSORS = (
"django.contrib.auth.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n",
"django.core.context_processors.media",
"django.core.context_processors.static",
"django.core.context_processors.tz",
"django.contrib.messages.context_processors.messages",
"django.core.context_processors.request",
)
AUTHENTICATION_BACKENDS = (
    'central.accounts.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
    
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
