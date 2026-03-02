# db/repositories/bookings.py
from __future__ import annotations

from typing import Optional, Iterable
from datetime import date, time
from decimal import Decimal

from sqlalchemy import select, and_, update, delete, func
from sqlalchemy.orm import Session

from data.config import current_time
from db.repositories.base import BaseRepository
from db.schemas.bookings import BookingsTable, BookingServicesTable
from db.schemas.services import ServicesTable
from db.schemas.payroll import WorkRecordsTable


class BookingsRepository(BaseRepository):
    table = BookingsTable

    @classmethod
    async def alist_by_client(cls, client_id: int, session: Session):
        with session:
            res = session.execute(select(cls.table).where(cls.table.client_id == client_id).order_by(cls.table.id.desc()))
            return res.scalars().all()

    @classmethod
    async def aget_full(cls, booking_id: int, session: Session) -> Optional[BookingsTable]:
        with session:
            return (session.execute(select(cls.table).where(cls.table.id == booking_id))).scalar()

    @classmethod
    async def acreate_booking(
        cls,
        *,
        client_id: int,
        vehicle_id: int,
        booking_date: date,
        booking_time: time,
        note: Optional[str],
        session: Session,
    ) -> BookingsTable:
        now = current_time().utcnow()
        with session:
            instance = cls.table(
                client_id=client_id,
                vehicle_id=vehicle_id,
                booking_date=booking_date,
                booking_time=booking_time,
                note=note,
                status="PENDING",
                updated_at=now,
            )
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance

    @classmethod
    async def arecalc_total(cls, booking_id: int, session: Session) -> Decimal:
        """
        total_amount = SUM(price * qty)
        """
        with session:
            total = session.execute(
                select(func.coalesce(func.sum(BookingServicesTable.price * BookingServicesTable.qty), 0))
                .where(BookingServicesTable.booking_id == booking_id)
            ).scalar()

            session.execute(
                update(cls.table).where(cls.table.id == booking_id).values(total_amount=total, updated_at=current_time().utcnow())
            )
            session.commit()
            return total


class BookingServicesRepository(BaseRepository):
    table = BookingServicesTable

    @classmethod
    async def alist_by_booking(cls, booking_id: int, session: Session):
        with session:
            res = session.execute(select(cls.table).where(cls.table.booking_id == booking_id).order_by(cls.table.id))
            return res.scalars().all()

    @classmethod
    async def aadd_service_line(
        cls,
        *,
        booking_id: int,
        service_id: int,
        qty: int = 1,
        price: Optional[Decimal] = None,
        session: Session,
    ) -> BookingServicesTable:
        """
        price berilmasa => service.price dan oladi.
        """
        now = current_time().utcnow()
        with session:
            if price is None:
                srv_price = (session.execute(select(ServicesTable.price).where(ServicesTable.id == service_id))).scalar()
                price = srv_price or Decimal("0")

            instance = cls.table(
                booking_id=booking_id,
                service_id=service_id,
                qty=qty,
                price=price,
                updated_at=now,
            )
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance

    @classmethod
    async def areplace_lines(
        cls,
        *,
        booking_id: int,
        items: Iterable[dict],
        session: Session,
    ):
        """
        items: [{"service_id": 1, "qty": 1, "price": None}, ...]
        - eski line'larni o‘chiradi
        - yangilarini qo‘shadi
        """
        with session:
            session.execute(delete(cls.table).where(cls.table.booking_id == booking_id))
            session.commit()

        for it in items:
            await cls.aadd_service_line(
                booking_id=booking_id,
                service_id=int(it["service_id"]),
                qty=int(it.get("qty", 1)),
                price=it.get("price"),
                session=session,
            )
        return True


class BookingWorkflowRepository:
    """
    Booking yakunlash / WorkRecord yaratish (TG botdan ishlatish uchun).
    """

    @classmethod
    async def acomplete_booking(
        cls,
        *,
        booking_id: int,
        employee_id: int,
        session: Session,
        kpi_percent_default: int = 10,
    ) -> Optional[BookingsTable]:
        """
        - booking total recalculation
        - status=COMPLETED, completed_at=now, employee_id set
        - WorkRecord upsert (booking unique)
        """
        now = current_time().utcnow()

        with session:
            booking = (session.execute(select(BookingsTable).where(BookingsTable.id == booking_id))).scalar()
            if not booking:
                return None

            if booking.status in ("CANCELLED", "COMPLETED"):
                return booking

            # total
            total = session.execute(
                select(func.coalesce(func.sum(BookingServicesTable.price * BookingServicesTable.qty), 0))
                .where(BookingServicesTable.booking_id == booking_id)
            ).scalar()

            session.execute(
                update(BookingsTable)
                .where(BookingsTable.id == booking_id)
                .values(
                    employee_id=employee_id,
                    status="COMPLETED",
                    completed_at=now,
                    total_amount=total,
                    updated_at=now,
                )
            )

            # WorkRecord upsert (booking_id unique)
            wr = (session.execute(select(WorkRecordsTable).where(WorkRecordsTable.booking_id == booking_id))).scalar()
            if wr:
                session.execute(
                    update(WorkRecordsTable)
                    .where(WorkRecordsTable.id == wr.id)
                    .values(
                        employee_id=employee_id,
                        amount=total,
                        updated_at=now,
                    )
                )
            else:
                new_wr = WorkRecordsTable(
                    employee_id=employee_id,
                    booking_id=booking_id,
                    amount=total,
                    kpi_percent=kpi_percent_default,
                    performed_at=now,
                    updated_at=now,
                )
                session.add(new_wr)

            session.commit()
            return (session.execute(select(BookingsTable).where(BookingsTable.id == booking_id))).scalar()