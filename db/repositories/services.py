# db/repositories/services.py
from __future__ import annotations

from typing import Optional

from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session

from db.repositories.base import BaseRepository
from db.schemas.services import (
    ServiceCategoriesTable,
    ServicesTable,
    services_service_allowed_brands,
    services_service_allowed_models,
)


class ServiceCategoriesRepository(BaseRepository):
    table = ServiceCategoriesTable

    @classmethod
    async def alist_active(cls, session: Session):
        with session:
            res = session.execute(select(cls.table).where(cls.table.is_active == True).order_by(cls.table.title))  # noqa: E712
            return res.scalars().all()


class ServicesRepository(BaseRepository):
    table = ServicesTable

    @classmethod
    async def aget_by_id(cls, service_id: int, session: Session) -> Optional[ServicesTable]:
        with session:
            return (session.execute(select(cls.table).where(cls.table.id == service_id))).scalar()

    @classmethod
    async def alist_active(cls, session: Session):
        with session:
            res = session.execute(select(cls.table).where(cls.table.is_active == True).order_by(cls.table.title))  # noqa: E712
            return res.scalars().all()

    @classmethod
    async def alist_allowed_for_vehicle(
        cls,
        *,
        brand_id: int,
        car_model_id: int,
        session: Session,
    ):
        """
        ServiceScope:
        - scope == "ALL" => hammasi
        - scope == "LIMITED" => allowed_models yoki allowed_brands mos bo‘lsa
        """
        with session:
            # LIMITED va model mos
            q_model = (
                select(ServicesTable)
                .join(services_service_allowed_models, services_service_allowed_models.c.service_id == ServicesTable.id)
                .where(services_service_allowed_models.c.carmodel_id == car_model_id)
            )

            # LIMITED va brand mos
            q_brand = (
                select(ServicesTable)
                .join(services_service_allowed_brands, services_service_allowed_brands.c.service_id == ServicesTable.id)
                .where(services_service_allowed_brands.c.brand_id == brand_id)
            )

            # ALL scope
            q_all = select(ServicesTable).where(ServicesTable.scope == "ALL")

            # hammasini union qilamiz
            res = session.execute(q_all.union(q_model).union(q_brand))
            return res.scalars().all()