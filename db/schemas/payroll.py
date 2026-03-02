# db/schemas/payroll.py
from __future__ import annotations

from typing import Optional, List
from decimal import Decimal
import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.config import BaseModel


class SalaryProfilesTable(BaseModel):
    __tablename__ = "payroll_salaryprofile"

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)

    employee_id: Mapped[int] = mapped_column(
        "employee_id",
        BigInteger,
        ForeignKey("users_employee.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    fixed_salary: Mapped[Decimal] = mapped_column(
        "fixed_salary",
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0"),
    )
    kpi_percent: Mapped[int] = mapped_column(
        "kpi_percent",
        Integer,
        nullable=False,
        default=10,
    )

    employee: Mapped["EmployeesTable"] = relationship("EmployeesTable", back_populates="salary_profile")


class WorkRecordsTable(BaseModel):
    __tablename__ = "payroll_workrecord"

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)

    employee_id: Mapped[int] = mapped_column(
        "employee_id",
        BigInteger,
        ForeignKey("users_employee.id", ondelete="PROTECT"),
        nullable=False,
    )

    booking_id: Mapped[int] = mapped_column(
        "booking_id",
        BigInteger,
        ForeignKey("bookings_booking.id", ondelete="PROTECT"),
        nullable=False,
        unique=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        "amount",
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0"),
    )

    kpi_percent: Mapped[int] = mapped_column(
        "kpi_percent",
        Integer,
        nullable=False,
        default=10,
    )

    kpi_amount: Mapped[Decimal] = mapped_column(
        "kpi_amount",
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0"),
    )

    performed_at: Mapped[datetime.datetime] = mapped_column(
        "performed_at",
        DateTime(timezone=False),
        nullable=False,
        default=datetime.datetime.utcnow,
    )

    employee: Mapped["EmployeesTable"] = relationship("EmployeesTable", back_populates="work_records")
    booking: Mapped["BookingsTable"] = relationship("BookingsTable", back_populates="work_record")

    __table_args__ = (
        Index("payroll_workrecord_performed_at_idx", "performed_at"),
    )


class PayrollMonthsTable(BaseModel):
    __tablename__ = "payroll_payrollmonth"

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)

    employee_id: Mapped[int] = mapped_column(
        "employee_id",
        BigInteger,
        ForeignKey("users_employee.id", ondelete="PROTECT"),
        nullable=False,
    )

    year: Mapped[int] = mapped_column("year", Integer, nullable=False)
    month: Mapped[int] = mapped_column("month", Integer, nullable=False)

    # ✅ NOT NULL bo‘lgani uchun python default beramiz
    fixed_salary_snapshot: Mapped[Decimal] = mapped_column(
        "fixed_salary_snapshot",
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0"),
    )

    works_total: Mapped[Decimal] = mapped_column(
        "works_total",
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0"),
    )

    kpi_total: Mapped[Decimal] = mapped_column(
        "kpi_total",
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0"),
    )

    total_salary: Mapped[Decimal] = mapped_column(
        "total_salary",
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0"),
    )

    employee: Mapped["EmployeesTable"] = relationship("EmployeesTable", back_populates="payroll_months")

    __table_args__ = (
        UniqueConstraint("employee_id", "year", "month", name="uniq_employee_year_month"),
    )