from .base import *

ALLOWED_HOSTS = ["ip-address", "www.your-website.com"]

DEBUG = False

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

THUMBNAIL_DEBUG = False  # incase we are using "sorl.thumbnail"
