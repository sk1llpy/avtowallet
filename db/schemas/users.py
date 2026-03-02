# apps/users.py
from __future__ import annotations

from typing import Optional, List
from sqlalchemy import BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.config import BaseModel  # sizda bor BaseModel


class UsersTable(BaseModel):
    __tablename__ = "users_user"

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)

    tg_id: Mapped[str] = mapped_column("tg_id", String(64), unique=True, nullable=False)
    tg_username: Mapped[Optional[str]] = mapped_column("tg_username", String(255), nullable=True)
    tg_full_name: Mapped[Optional[str]] = mapped_column("tg_full_name", String(255), nullable=True)

    first_name: Mapped[Optional[str]] = mapped_column("first_name", String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column("last_name", String(255), nullable=True)
    phone_number: Mapped[str] = mapped_column("phone_number", String(255), nullable=False)

    # relations
    vehicles: Mapped[List["VehiclesTable"]] = relationship("VehiclesTable", back_populates="owner")
    bookings: Mapped[List["BookingsTable"]] = relationship("BookingsTable", back_populates="client")
    employee_profile: Mapped[Optional["EmployeesTable"]] = relationship(
        "EmployeesTable", back_populates="user", uselist=False
    )


class EmployeesTable(BaseModel):
    __tablename__ = "users_employee"

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        "user_id",
        BigInteger,
        ForeignKey("users_user.id", ondelete="PROTECT"),
        nullable=False,
        unique=True,
    )

    position: Mapped[Optional[str]] = mapped_column("position", String(120), nullable=True)
    is_master: Mapped[bool] = mapped_column("is_master", Boolean, nullable=False, server_default="true")
    is_manager: Mapped[bool] = mapped_column("is_manager", Boolean, nullable=False, server_default="false")

    # relations
    user: Mapped["UsersTable"] = relationship("UsersTable", back_populates="employee_profile")
    assigned_bookings: Mapped[List["BookingsTable"]] = relationship("BookingsTable", back_populates="employee")

    salary_profile: Mapped[Optional["SalaryProfilesTable"]] = relationship(
        "SalaryProfilesTable", back_populates="employee", uselist=False
    )
    work_records: Mapped[List["WorkRecordsTable"]] = relationship("WorkRecordsTable", back_populates="employee")
    payroll_months: Mapped[List["PayrollMonthsTable"]] = relationship("PayrollMonthsTable", back_populates="employee")