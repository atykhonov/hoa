DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hoa2',
        'USER': 'hoa',
        'PASSWORD': 'URi2QE',
        'PORT': '',
    }
}

ALLOWED_HOSTS = [
    'api.hoa.com.ua',
]

CORS_ORIGIN_WHITELIST = (
    'hoa.com.ua',
)
