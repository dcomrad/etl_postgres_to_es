import os

from dotenv import load_dotenv

load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PG_DB_NAME'),
        'USER': os.getenv('PG_DB_USER'),
        'PASSWORD': os.getenv('PG_DB_PASSWORD'),
        'HOST': os.getenv('PG_DB_HOST'),
        'PORT': os.getenv('PG_DB_PORT'),
        'OPTIONS': {
           'options': '-c search_path=public,content'
        }
    }
}
