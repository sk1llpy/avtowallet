# db/repository.py

# Base
from db.repositories.base import BaseRepository

# Users
from db.repositories.users import (
    UsersRepository,
    EmployeesRepository,
)

# Vehicles
from db.repositories.vehicles import (
    BrandsRepository,
    CarModelsRepository,
    VehiclesRepository,
)

# Services
from db.repositories.services import (
    ServiceCategoriesRepository,
    ServicesRepository,
)

# Bookings
from db.repositories.bookings import (
    BookingsRepository,
    BookingServicesRepository,
    BookingWorkflowRepository,
)

# Payroll
from db.repositories.payroll import (
    SalaryProfilesRepository,
    WorkRecordsRepository,
    PayrollMonthsRepository,
)

__all__ = [
    # Base
    "BaseRepository",

    # Users
    "UsersRepository",
    "EmployeesRepository",

    # Vehicles
    "BrandsRepository",
    "CarModelsRepository",
    "VehiclesRepository",

    # Services
    "ServiceCategoriesRepository",
    "ServicesRepository",

    # Bookings
    "BookingsRepository",
    "BookingServicesRepository",
    "BookingWorkflowRepository",

    # Payroll
    "SalaryProfilesRepository",
    "WorkRecordsRepository",
    "PayrollMonthsRepository",
]