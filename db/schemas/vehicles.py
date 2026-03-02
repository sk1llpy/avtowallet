# apps/vehicles.py
from __future__ import annotations

from typing import Optional, List
from sqlalchemy import BigInteger, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.config import BaseModel


class BrandsTable(BaseModel):
    __tablename__ = "vehicles_brand"

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column("name", String(120), unique=True, nullable=False)

    models: Mapped[List["CarModelsTable"]] = relationship("CarModelsTable", back_populates="brand")
    vehicles: Mapped[List["VehiclesTable"]] = relationship("VehiclesTable", back_populates="brand")

    allowed_services: Mapped[List["ServicesTable"]] = relationship(
        "ServicesTable",
        secondary="services_service_allowed_brands",
        back_populates="allowed_brands",
    )


class CarModelsTable(BaseModel):
    __tablename__ = "vehicles_carmodel"

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)

    brand_id: Mapped[int] = mapped_column(
        "brand_id",
        BigInteger,
        ForeignKey("vehicles_brand.id", ondelete="PROTECT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column("name", String(120), nullable=False)

    brand: Mapped["BrandsTable"] = relationship("BrandsTable", back_populates="models")
    vehicles: Mapped[List["VehiclesTable"]] = relationship("VehiclesTable", back_populates="car_model")

    allowed_services: Mapped[List["ServicesTable"]] = relationship(
        "ServicesTable",
        secondary="services_service_allowed_models",
        back_populates="allowed_models",
    )

    __table_args__ = (
        UniqueConstraint("brand_id", "name", name="uniq_brand_model_name"),
    )


class VehiclesTable(BaseModel):
    __tablename__ = "vehicles_vehicle"

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)

    owner_id: Mapped[int] = mapped_column(
        "owner_id",
        BigInteger,
        ForeignKey("users_user.id", ondelete="CASCADE"),
        nullable=False,
    )
    brand_id: Mapped[int] = mapped_column(
        "brand_id",
        BigInteger,
        ForeignKey("vehicles_brand.id", ondelete="PROTECT"),
        nullable=False,
    )
    car_model_id: Mapped[int] = mapped_column(
        "car_model_id",
        BigInteger,
        ForeignKey("vehicles_carmodel.id", ondelete="PROTECT"),
        nullable=False,
    )

    plate_number: Mapped[str] = mapped_column("plate_number", String(32), nullable=False)
    color: Mapped[Optional[str]] = mapped_column("color", String(64), nullable=True)
    year: Mapped[Optional[int]] = mapped_column("year", Integer, nullable=True)

    owner: Mapped["UsersTable"] = relationship("UsersTable", back_populates="vehicles")
    brand: Mapped["BrandsTable"] = relationship("BrandsTable", back_populates="vehicles")
    car_model: Mapped["CarModelsTable"] = relationship("CarModelsTable", back_populates="vehicles")

    bookings: Mapped[List["BookingsTable"]] = relationship("BookingsTable", back_populates="vehicle")

    __table_args__ = (
        UniqueConstraint("owner_id", "plate_number", name="uniq_owner_plate"),
    )