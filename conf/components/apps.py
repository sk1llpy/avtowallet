INSTALLED_APPS = [
    # =========================
    # Unfold (Admin UI)
    # =========================
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",

    # =========================
    # Django base apps
    # =========================
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # =========================
    # Local apps (your project)
    # =========================
    "apps.general.apps.GeneralConfig",
    "apps.users.apps.UsersConfig",
    "apps.vehicles.apps.VehiclesConfig",
    "apps.services.apps.ServicesConfig",
    "apps.bookings.apps.BookingsConfig",
    "apps.payroll.apps.PayrollConfig",
]