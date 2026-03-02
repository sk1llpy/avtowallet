# db/repositories/users.py
from __future__ import annotations

from typing import Optional, Any

from sqlalchemy import select, and_, update
from sqlalchemy.orm import Session

from data.config import current_time
from db.repositories.base import BaseRepository
from db.schemas.users import UsersTable, EmployeesTable


class UsersRepository(BaseRepository):
    table = UsersTable

    # -------- ASYNC CUSTOMS (sync Session ishlaydi) --------
    @classmethod
    async def aget_by_tg_id(cls, tg_id: str, session: Session) -> Optional[UsersTable]:
        with session:
            return (session.execute(select(cls.table).where(cls.table.tg_id == tg_id))).scalar()

    @classmethod
    async def aupsert_from_telegram(
        cls,
        *,
        tg_id: str,
        tg_username: Optional[str],
        tg_full_name: Optional[str],
        phone_number: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        session: Session,
    ) -> UsersTable:
        """
        tg_id unique bo‘yicha:
        - bor bo‘lsa update
        - bo‘lmasa create
        """
        now = current_time().utcnow()

        with session:
            user = (session.execute(select(cls.table).where(cls.table.tg_id == tg_id))).scalar()

            if user:
                edits: dict[str, Any] = {
                    "tg_username": tg_username,
                    "tg_full_name": tg_full_name,
                    "updated_at": now,
                }
                if phone_number is not None:
                    edits["phone_number"] = phone_number
                if first_name is not None:
                    edits["first_name"] = first_name
                if last_name is not None:
                    edits["last_name"] = last_name

                session.execute(update(cls.table).where(cls.table.id == user.id).values(**edits))
                session.commit()

                return (session.execute(select(cls.table).where(cls.table.id == user.id))).scalar()

            params: dict[str, Any] = {
                "tg_id": tg_id,
                "tg_username": tg_username,
                "tg_full_name": tg_full_name,
                "phone_number": phone_number or "",
                "first_name": first_name,
                "last_name": last_name,
                "updated_at": now,
            }
            instance = cls.table(**params)
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance


class EmployeesRepository(BaseRepository):
    table = EmployeesTable

    @classmethod
    async def aget_by_user_id(cls, user_id: int, session: Session) -> Optional[EmployeesTable]:
        with session:
            return (session.execute(select(cls.table).where(cls.table.user_id == user_id))).scalar()

    @classmethod
    async def alist_masters_active(cls, session: Session):
        with session:
            res = session.execute(
                select(cls.table).where(and_(cls.table.is_master == True, cls.table.is_active == True))  # noqa: E712
            )
            return res.scalars().all()
