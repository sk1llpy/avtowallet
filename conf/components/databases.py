from data.config import PostgresSettings

psql = PostgresSettings()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": psql.name,
        "USER": psql.user,
        "PASSWORD": psql.password,
        "HOST": psql.host,
        "PORT": psql.port,
        'DISABLE_SERVER_SIDE_CURSORS': True,
    }
}