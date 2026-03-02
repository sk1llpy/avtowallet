# apps/bookings.py
from __future__ import annotations

from typing import Optional, List
from datetime import datetime, date, time
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    Time,
    Integer,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.config import BaseModel


class BookingsTable(BaseModel):
    __tablename__ = "bookings_booking"

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)

    client_id: Mapped[int] = mapped_column(
        "client_id",
        BigInteger,
        ForeignKey("users_user.id", ondelete="PROTECT"),
        nullable=False,
    )
    vehicle_id: Mapped[int] = mapped_column(
        "vehicle_id",
        BigInteger,
        ForeignKey("vehicles_vehicle.id", ondelete="PROTECT"),
        nullable=False,
    )

    booking_date: Mapped[date] = mapped_column("booking_date", Date, nullable=False)
    booking_time: Mapped[time] = mapped_column("booking_time", Time, nullable=False)

    status: Mapped[str] = mapped_column("status", String(20), nullable=False, server_default="PENDING")

    employee_id: Mapped[Optional[int]] = mapped_column(
        "employee_id",
        BigInteger,
        ForeignKey("users_employee.id", ondelete="PROTECT"),
        nullable=True,
    )

    note: Mapped[Optional[str]] = mapped_column("note", Text, nullable=True)

    completed_at: Mapped[Optional[datetime]] = mapped_column("completed_at", DateTime(timezone=True), nullable=True)
    total_amount: Mapped[Optional[Decimal]] = mapped_column("total_amount", Numeric(14, 2), nullable=True)

    client: Mapped["UsersTable"] = relationship("UsersTable", back_populates="bookings")
    vehicle: Mapped["VehiclesTable"] = relationship("VehiclesTable", back_populates="bookings")
    employee: Mapped[Optional["EmployeesTable"]] = relationship("EmployeesTable", back_populates="assigned_bookings")

    booking_services: Mapped[List["BookingServicesTable"]] = relationship(
        "BookingServicesTable",
        back_populates="booking",
        cascade="all, delete-orphan",
    )

    work_record: Mapped[Optional["WorkRecordsTable"]] = relationship(
        "WorkRecordsTable",
        back_populates="booking",
        uselist=False,
    )

    __table_args__ = (
        Index("bookings_booking_booking_date_booking_time_idx", "booking_date", "booking_time"),
        Index("bookings_booking_status_idx", "status"),
    )


class BookingServicesTable(BaseModel):
    __tablename__ = "bookings_bookingservice"

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)

    booking_id: Mapped[int] = mapped_column(
        "booking_id",
        BigInteger,
        ForeignKey("bookings_booking.id", ondelete="CASCADE"),
        nullable=False,
    )
    service_id: Mapped[int] = mapped_column(
        "service_id",
        BigInteger,
        ForeignKey("services_service.id", ondelete="PROTECT"),
        nullable=False,
    )

    qty: Mapped[int] = mapped_column("qty", Integer, nullable=False, server_default="1", default=1)
    price: Mapped[Optional[Decimal]] = mapped_column("price", Numeric(14, 2), nullable=True)

    booking: Mapped["BookingsTable"] = relationship("BookingsTable", back_populates="booking_services")
    service: Mapped["ServicesTable"] = relationship("ServicesTable", back_populates="booking_lines")

    __table_args__ = (
        CheckConstraint("qty >= 1", name="bookings_bookingservice_qty_gte_1"),
    )