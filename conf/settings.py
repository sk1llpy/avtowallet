from split_settings.tools import include

include(
    'components/__init__.py',
    'components/auth.py',
    'components/middlewares.py',
    'components/apps.py',
    'components/databases.py',
    'components/templates.py',
    'components/internationalization.py',
)