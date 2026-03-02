import os
from pathlib import Path
from datetime import timedelta

from data.config import DjangoSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

django = DjangoSettings()

SECRET_KEY = django.secret_key
DEBUG = django.debug

ALLOWED_HOSTS = django.allowed_hosts_list

CSRF_TRUSTED_ORIGINS = django.csrf_trusted_origins_list

ROOT_URLCONF = "conf.urls"
WSGI_APPLICATION = "conf.wsgi.application"

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # development uchun

MEDIA_URL = '/uploads/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# settings.py
UNFOLD = {
    "SITE_TITLE": "AvtoWallet Admin",
    "SITE_HEADER": "AvtoWallet",
    "SITE_URL": "/",
    "SITE_SYMBOL": "directions_car",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "SHOW_DELETE_BUTTON": True,

    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Foydalanuvchilar",
                "icon": "group",
                "items": [
                    {"title": "Telegram foydalanuvchilar", "link": "/admin/users/user/"},
                    {"title": "Ishchilar", "link": "/admin/users/employee/"},
                ],
            },
            {
                "title": "Avtomobillar",
                "icon": "directions_car",
                "items": [
                    {"title": "Brendlar", "link": "/admin/vehicles/brand/"},
                    {"title": "Modellar", "link": "/admin/vehicles/carmodel/"},
                    {"title": "Avtomobillar", "link": "/admin/vehicles/vehicle/"},
                ],
            },
            {
                "title": "Xizmatlar",
                "icon": "build",
                "items": [
                    {"title": "Kategoriyalar", "link": "/admin/services/servicecategory/"},
                    {"title": "Xizmatlar ro‘yxati", "link": "/admin/services/service/"},
                ],
            },
            {
                "title": "Bronlar",
                "icon": "event",
                "items": [
                    {"title": "Bronlar", "link": "/admin/bookings/booking/"},
                    {"title": "Bron xizmatlari", "link": "/admin/bookings/bookingservice/"},
                ],
            },
            {
                "title": "Maosh / KPI",
                "icon": "payments",
                "items": [
                    {"title": "Maosh sozlamalari", "link": "/admin/payroll/salaryprofile/"},
                    {"title": "Ish yozuvlari", "link": "/admin/payroll/workrecord/"},
                    {"title": "Oylik hisoblar", "link": "/admin/payroll/payrollmonth/"},
                ],
            },
        ],
    },
}

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]