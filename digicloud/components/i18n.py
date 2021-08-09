from .common import *

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = env("LANGUAGE_CODE", default="en-us")

TIME_ZONE = env("TIME_ZONE", default="UTC")

USE_I18N = True

USE_L10N = True

USE_TZ = True
