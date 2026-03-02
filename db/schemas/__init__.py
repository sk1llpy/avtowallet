# Users
from .users import UsersTable, EmployeesTable

# Vehicles
from .vehicles import BrandsTable, CarModelsTable, VehiclesTable

# Services
from .services import ServiceCategoriesTable, ServicesTable

# Bookings
from .bookings import BookingsTable, BookingServicesTable

# Payroll
from .payroll import SalaryProfilesTable, WorkRecordsTable, PayrollMonthsTable

__all__ = [
    # Users
    "UsersTable",
    "EmployeesTable",

    # Vehicles
    "BrandsTable",
    "CarModelsTable",
    "VehiclesTable",

    # Services
    "ServiceCategoriesTable",
    "ServicesTable",

    # Bookings
    "BookingsTable",
    "BookingServicesTable",

    # Payroll
    "SalaryProfilesTable",
    "WorkRecordsTable",
    "PayrollMonthsTable",
]