# db/schemas/services.py
from __future__ import annotations

from typing import Optional, List
from decimal import Decimal

from sqlalchemy import (
    Table,
    Column,
    BigInteger,
    ForeignKey,
    String,
    Integer,
    Numeric,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.config import BaseModel  # sizda bor BaseModel

# db/schemas/services.py
class ServiceScope:
    ALL = "ALL"
    LIMITED = "LIMITED"

# ✅ Django auto M2M tables (Table => Column ishlatiladi)
services_service_allowed_brands = Table(
    "services_service_allowed_brands",
    BaseModel.metadata,
    Column("id", BigInteger, primary_key=True),
    Column("service_id", BigInteger, ForeignKey("services_service.id", ondelete="CASCADE"), nullable=False),
    Column("brand_id", BigInteger, ForeignKey("vehicles_brand.id", ondelete="CASCADE"), nullable=False),
    UniqueConstraint("service_id", "brand_id"),
)

services_service_allowed_models = Table(
    "services_service_allowed_models",
    BaseModel.metadata,
    Column("id", BigInteger, primary_key=True),
    Column("service_id", BigInteger, ForeignKey("services_service.id", ondelete="CASCADE"), nullable=False),
    Column("carmodel_id", BigInteger, ForeignKey("vehicles_carmodel.id", ondelete="CASCADE"), nullable=False),
    UniqueConstraint("service_id", "carmodel_id"),
)


class ServiceCategoriesTable(BaseModel):
    __tablename__ = "services_servicecategory"

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column("title", String(120), unique=True, nullable=False)

    services: Mapped[List["ServicesTable"]] = relationship("ServicesTable", back_populates="category")


class ServicesTable(BaseModel):
    __tablename__ = "services_service"

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)

    category_id: Mapped[Optional[int]] = mapped_column(
        "category_id",
        BigInteger,
        ForeignKey("services_servicecategory.id", ondelete="PROTECT"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column("title", String(200), nullable=False)
    price: Mapped[Decimal] = mapped_column("price", Numeric(14, 2), nullable=False, server_default="0")

    scope: Mapped[str] = mapped_column("scope", String(20), nullable=False, server_default="ALL")
    duration_minutes: Mapped[Optional[int]] = mapped_column("duration_minutes", Integer, nullable=True)

    category: Mapped[Optional["ServiceCategoriesTable"]] = relationship("ServiceCategoriesTable", back_populates="services")

    allowed_brands: Mapped[List["BrandsTable"]] = relationship(
        "BrandsTable",
        secondary=services_service_allowed_brands,
        back_populates="allowed_services",
    )

    allowed_models: Mapped[List["CarModelsTable"]] = relationship(
        "CarModelsTable",
        secondary=services_service_allowed_models,
        back_populates="allowed_services",
    )

    booking_lines: Mapped[List["BookingServicesTable"]] = relationship("BookingServicesTable", back_populates="service")

    __table_args__ = (
        Index("services_service_title_idx", "title"),
        Index("services_service_scope_idx", "scope"),
    )