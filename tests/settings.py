import os

os.environ["DJANGO_DEBUG"] = "1"  # no secret key or HTTPS needed under test (pytest-django turns DEBUG off)

from config.settings import *  # noqa: F403

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]  # fast, tests only
