# db/repositories/vehicles.py
from __future__ import annotations

from typing import Optional

from sqlalchemy import select, and_, update
from sqlalchemy.orm import Session

from data.config import current_time
from db.repositories.base import BaseRepository
from db.schemas.vehicles import BrandsTable, CarModelsTable, VehiclesTable


class BrandsRepository(BaseRepository):
    table = BrandsTable

    @classmethod
    async def aget_by_name(cls, name: str, session: Session) -> Optional[BrandsTable]:
        with session:
            return (session.execute(select(cls.table).where(cls.table.name == name))).scalar()

    @classmethod
    async def aget_or_create_by_name(cls, name: str, session: Session) -> BrandsTable:
        now = current_time().utcnow()
        with session:
            obj = (session.execute(select(cls.table).where(cls.table.name == name))).scalar()
            if obj:
                return obj
            instance = cls.table(name=name, updated_at=now)
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance


class CarModelsRepository(BaseRepository):
    table = CarModelsTable

    @classmethod
    async def aget_by_brand_and_name(cls, brand_id: int, name: str, session: Session) -> Optional[CarModelsTable]:
        with session:
            return (
                session.execute(
                    select(cls.table).where(and_(cls.table.brand_id == brand_id, cls.table.name == name))
                )
            ).scalar()

    @classmethod
    async def aget_or_create(cls, brand_id: int, name: str, session: Session) -> CarModelsTable:
        now = current_time().utcnow()
        with session:
            obj = (
                session.execute(
                    select(cls.table).where(and_(cls.table.brand_id == brand_id, cls.table.name == name))
                )
            ).scalar()
            if obj:
                return obj
            instance = cls.table(brand_id=brand_id, name=name, updated_at=now)
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance

    @classmethod
    async def alist_by_brand(cls, brand_id: int, session: Session):
        with session:
            res = session.execute(select(cls.table).where(cls.table.brand_id == brand_id).order_by(cls.table.name))
            return res.scalars().all()


class VehiclesRepository(BaseRepository):
    table = VehiclesTable

    @classmethod
    async def alist_by_owner(cls, owner_id: int, session: Session):
        with session:
            res = session.execute(select(cls.table).where(cls.table.owner_id == owner_id).order_by(cls.table.id.desc()))
            return res.scalars().all()

    @classmethod
    async def aget_by_owner_and_plate(cls, owner_id: int, plate_number: str, session: Session) -> Optional[VehiclesTable]:
        with session:
            return (
                session.execute(
                    select(cls.table).where(and_(cls.table.owner_id == owner_id, cls.table.plate_number == plate_number))
                )
            ).scalar()

    @classmethod
    async def aupsert_vehicle(
        cls,
        *,
        owner_id: int,
        brand_id: int,
        car_model_id: int,
        plate_number: str,
        year: Optional[int],
        color: Optional[str],
        session: Session,
    ) -> VehiclesTable:
        now = current_time().utcnow()
        with session:
            vehicle = (
                session.execute(
                    select(cls.table).where(and_(cls.table.owner_id == owner_id, cls.table.plate_number == plate_number))
                )
            ).scalar()

            if vehicle:
                session.execute(
                    update(cls.table)
                    .where(cls.table.id == vehicle.id)
                    .values(
                        brand_id=brand_id,
                        car_model_id=car_model_id,
                        year=year,
                        color=color,
                        updated_at=now,
                    )
                )
                session.commit()
                return (session.execute(select(cls.table).where(cls.table.id == vehicle.id))).scalar()

            instance = cls.table(
                owner_id=owner_id,
                brand_id=brand_id,
                car_model_id=car_model_id,
                plate_number=plate_number,
                year=year,
                color=color,
                updated_at=now,
            )
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance