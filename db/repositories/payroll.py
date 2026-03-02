# db/repositories/payroll.py
from __future__ import annotations

from typing import Optional
from decimal import Decimal
from datetime import datetime

from sqlalchemy import select, and_, update, func
from sqlalchemy.orm import Session

from data.config import current_time
from db.repositories.base import BaseRepository
from db.schemas.payroll import SalaryProfilesTable, WorkRecordsTable, PayrollMonthsTable


class SalaryProfilesRepository(BaseRepository):
    table = SalaryProfilesTable

    @classmethod
    async def aget_by_employee(cls, employee_id: int, session: Session) -> Optional[SalaryProfilesTable]:
        with session:
            return (session.execute(select(cls.table).where(cls.table.employee_id == employee_id))).scalar()


class WorkRecordsRepository(BaseRepository):
    table = WorkRecordsTable

    @classmethod
    async def alist_by_employee_month(cls, employee_id: int, year: int, month: int, session: Session):
        with session:
            res = session.execute(
                select(cls.table)
                .where(
                    and_(
                        cls.table.employee_id == employee_id,
                        func.extract("year", cls.table.performed_at) == year,
                        func.extract("month", cls.table.performed_at) == month,
                    )
                )
                .order_by(cls.table.performed_at.desc())
            )
            return res.scalars().all()


class PayrollMonthsRepository(BaseRepository):
    table = PayrollMonthsTable

    @classmethod
    async def aget_or_create_month(cls, employee_id: int, year: int, month: int, session: Session) -> PayrollMonthsTable:
        now = current_time().utcnow()
        with session:
            pm = (
                session.execute(
                    select(cls.table).where(
                        and_(cls.table.employee_id == employee_id, cls.table.year == year, cls.table.month == month)
                    )
                )
            ).scalar()

            if pm:
                return pm

            instance = cls.table(employee_id=employee_id, year=year, month=month, updated_at=now)
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance

    @classmethod
    async def arecalc_month(cls, employee_id: int, year: int, month: int, session: Session) -> PayrollMonthsTable:
        """
        - fixed_salary_snapshot: SalaryProfile.fixed_salary (yoki 0)
        - works_total: SUM(WorkRecord.amount)
        - kpi_total: SUM(WorkRecord.kpi_amount)
        - total_salary: fixed + kpi_total
        """
        now = current_time().utcnow()

        with session:
            pm = (
                session.execute(
                    select(cls.table).where(
                        and_(cls.table.employee_id == employee_id, cls.table.year == year, cls.table.month == month)
                    )
                )
            ).scalar()

            if not pm:
                pm = cls.table(employee_id=employee_id, year=year, month=month, updated_at=now)
                session.add(pm)
                session.commit()
                session.refresh(pm)

            sp = (session.execute(select(SalaryProfilesTable).where(SalaryProfilesTable.employee_id == employee_id))).scalar()
            fixed = (sp.fixed_salary if sp else Decimal("0"))

            works_total = session.execute(
                select(func.coalesce(func.sum(WorkRecordsTable.amount), 0))
                .where(
                    and_(
                        WorkRecordsTable.employee_id == employee_id,
                        func.extract("year", WorkRecordsTable.performed_at) == year,
                        func.extract("month", WorkRecordsTable.performed_at) == month,
                    )
                )
            ).scalar()

            kpi_total = session.execute(
                select(func.coalesce(func.sum(WorkRecordsTable.kpi_amount), 0))
                .where(
                    and_(
                        WorkRecordsTable.employee_id == employee_id,
                        func.extract("year", WorkRecordsTable.performed_at) == year,
                        func.extract("month", WorkRecordsTable.performed_at) == month,
                    )
                )
            ).scalar()

            total_salary = fixed + (kpi_total or Decimal("0"))

            session.execute(
                update(cls.table)
                .where(cls.table.id == pm.id)
                .values(
                    fixed_salary_snapshot=fixed,
                    works_total=works_total,
                    kpi_total=kpi_total,
                    total_salary=total_salary,
                    updated_at=now,
                )
            )
            session.commit()

            return (session.execute(select(cls.table).where(cls.table.id == pm.id))).scalar()