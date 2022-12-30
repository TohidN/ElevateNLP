from .base import *

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

DEBUG = True

# Email Testing using file logs
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = os.path.join(BASE_DIR, "emails")

# debug for "sorl.thumbnail"
THUMBNAIL_DEBUG = True

# Allow Jupiter to show results
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
