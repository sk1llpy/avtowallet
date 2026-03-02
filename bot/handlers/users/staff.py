# bot/handlers/users/staff.py
from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Optional

from aiogram import F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session

from bot.decorators import create_session
from bot.routers import users as router

from db.repository import (
    UsersRepository,
    EmployeesRepository,
    PayrollMonthsRepository,
    WorkRecordsRepository,
)

from db.schemas.bookings import BookingsTable
from db.schemas.payroll import WorkRecordsTable
from db.schemas.vehicles import VehiclesTable
from db.schemas.users import EmployeesTable, UsersTable

from bot.keyboards.default import menu as menu_kb


# =========================
# STAFF MENU (buttons)
# =========================
BTN_SALARY = "📊 Oyliklarim"
BTN_COMPLETED = "✅ Bajarilgan bronlar"
BTN_TODAY = "📅 Bugungi bronlar"
BTN_WORKS = "🧾 Mening ishlarim"
BTN_PROFILE = "👤 Profil"
BTN_HOME = "🏠 Asosiy"


def staff_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_SALARY), KeyboardButton(text=BTN_COMPLETED)],
            [KeyboardButton(text=BTN_TODAY), KeyboardButton(text=BTN_WORKS)],
            [KeyboardButton(text=BTN_PROFILE), KeyboardButton(text=BTN_HOME)],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=True,
    )


# =========================
# HELPERS
# =========================
def local_now() -> datetime.datetime:
    # Sizning timezone +5 (Toshkent)
    return datetime.datetime.utcnow() + datetime.timedelta(hours=5)


def format_money(x: Decimal | int | float | None) -> str:
    if x is None:
        return "0"
    try:
        val = Decimal(str(x))
    except Exception:
        return str(x)
    # 1200000.00 -> 1 200 000
    s = f"{val:.0f}"
    parts = []
    while s:
        parts.append(s[-3:])
        s = s[:-3]
    return " ".join(reversed(parts))


async def get_employee_or_deny(message: Message, session: Session) -> Optional[EmployeesTable]:
    tg_id = str(message.from_user.id)
    user = UsersRepository.get("tg_id", tg_id, session)
    if not user:
        # ro'yxatdan o'tmagan
        kb = await menu_kb.button()
        await message.answer(
            "❌ <b>Siz ro‘yxatdan o‘tmagansiz.</b>\n\n"
            "Iltimos <b>/start</b> ni bosing.",
            reply_markup=kb,
            parse_mode="HTML",
        )
        return None

    emp = EmployeesRepository.get("user_id", user.id, session)
    if not emp:
        # staff emas
        kb = await menu_kb.button()
        await message.answer(
            "⛔ <b>Sizda xodim paneliga ruxsat yo‘q.</b>\n\n"
            "Asosiy menyu ochildi 👇",
            reply_markup=kb,
            parse_mode="HTML",
        )
        return None

    return emp


# =========================
# STAFF: HOME
# =========================
@router.message(F.text == BTN_HOME)
@create_session
async def staff_home(message: Message, session: Session):
    emp = await get_employee_or_deny(message, session)
    if not emp:
        return

    await message.answer(
        "👷‍♂️ <b>Xodim paneli</b>\n\n"
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=staff_menu_kb(),
        parse_mode="HTML",
    )


# =========================
# STAFF: PROFILE
# =========================
@router.message(F.text == BTN_PROFILE)
@create_session
async def staff_profile(message: Message, session: Session):
    emp = await get_employee_or_deny(message, session)
    if not emp:
        return

    # user info
    with session:
        u = session.execute(select(UsersTable).where(UsersTable.id == emp.user_id)).scalar()

    roles = []
    if getattr(emp, "is_master", False):
        roles.append("🛠 Usta")
    if getattr(emp, "is_manager", False):
        roles.append("🧑‍💼 Menejer")
    role_txt = ", ".join(roles) if roles else "—"

    await message.answer(
        "👤 <b>Profil</b>\n\n"
        f"🆔 <b>ID:</b> {emp.id}\n"
        f"📌 <b>Lavozim:</b> {getattr(emp, 'position', None) or '—'}\n"
        f"🎭 <b>Rollar:</b> {role_txt}\n\n"
        f"📱 <b>Telefon:</b> {getattr(u, 'phone_number', '—') if u else '—'}\n"
        f"🙋‍♂️ <b>Ism:</b> {(getattr(u, 'first_name', None) or getattr(u, 'tg_full_name', None) or '—') if u else '—'}\n",
        reply_markup=staff_menu_kb(),
        parse_mode="HTML",
    )


# =========================
# STAFF: SALARY (current month)
# =========================
@router.message(F.text == BTN_SALARY)
@create_session
async def staff_salary(message: Message, session: Session):
    emp = await get_employee_or_deny(message, session)
    if not emp:
        return

    now = local_now()
    year, month = now.year, now.month

    # ✅ oy bo‘yicha qayta hisoblab beramiz (sizning repository async, session sync)
    pm = await PayrollMonthsRepository.arecalc_month(employee_id=emp.id, year=year, month=month, session=session)

    # last 5 works
    with session:
        wrs = (
            session.execute(
                select(WorkRecordsTable)
                .where(WorkRecordsTable.employee_id == emp.id)
                .order_by(WorkRecordsTable.performed_at.desc())
                .limit(5)
            )
        ).scalars().all()

    works_preview = ""
    if wrs:
        lines = []
        for wr in wrs:
            dt = wr.performed_at.strftime("%d.%m %H:%M") if wr.performed_at else "—"
            lines.append(
                f"• <b>{dt}</b> — ish: <b>{format_money(wr.amount)}</b> so‘m, "
                f"KPI: <b>{format_money(wr.kpi_amount)}</b> so‘m"
            )
        works_preview = "\n".join(lines)
    else:
        works_preview = "• Hozircha ish yozuvlari yo‘q."

    await message.answer(
        "📊 <b>Oyliklarim</b>\n\n"
        f"📅 <b>Davr:</b> {year}-{month:02d}\n\n"
        f"💵 <b>Fiks oylik:</b> <b>{format_money(pm.fixed_salary_snapshot)}</b> so‘m\n"
        f"🧾 <b>Ishlar summasi:</b> <b>{format_money(pm.works_total)}</b> so‘m\n"
        f"🎯 <b>KPI:</b> <b>{format_money(pm.kpi_total)}</b> so‘m\n"
        f"✅ <b>Jami oylik:</b> <b>{format_money(pm.total_salary)}</b> so‘m\n\n"
        "⏱ <b>Oxirgi ishlar:</b>\n"
        f"{works_preview}",
        reply_markup=staff_menu_kb(),
        parse_mode="HTML",
    )


# =========================
# STAFF: COMPLETED BOOKINGS (last 10)
# =========================
@router.message(F.text == BTN_COMPLETED)
@create_session
async def staff_completed_bookings(message: Message, session: Session):
    emp = await get_employee_or_deny(message, session)
    if not emp:
        return

    with session:
        rows = (
            session.execute(
                select(
                    BookingsTable.id,
                    BookingsTable.booking_date,
                    BookingsTable.booking_time,
                    BookingsTable.total_amount,
                    VehiclesTable.plate_number,
                )
                .join(VehiclesTable, VehiclesTable.id == BookingsTable.vehicle_id)
                .where(
                    and_(
                        BookingsTable.employee_id == emp.id,
                        BookingsTable.status == "COMPLETED",
                    )
                )
                .order_by(BookingsTable.completed_at.desc().nullslast(), BookingsTable.id.desc())
                .limit(10)
            )
        ).all()

    if not rows:
        await message.answer(
            "✅ <b>Bajarilgan bronlar</b>\n\n"
            "Hozircha <b>bajarilgan bron</b> topilmadi.",
            reply_markup=staff_menu_kb(),
            parse_mode="HTML",
        )
        return

    lines = []
    for b_id, b_date, b_time, total, plate in rows:
        d = b_date.strftime("%d.%m.%Y") if b_date else "—"
        t = b_time.strftime("%H:%M") if b_time else "—"
        lines.append(f"• <b>#{b_id}</b> — 🚗 <b>{plate}</b> — 🗓 {d} {t} — 💰 <b>{format_money(total)}</b> so‘m")

    await message.answer(
        "✅ <b>Bajarilgan bronlar</b>\n\n" + "\n".join(lines),
        reply_markup=staff_menu_kb(),
        parse_mode="HTML",
    )


# =========================
# STAFF: TODAY BOOKINGS
# =========================
@router.message(F.text == BTN_TODAY)
@create_session
async def staff_today_bookings(message: Message, session: Session):
    emp = await get_employee_or_deny(message, session)
    if not emp:
        return

    today = local_now().date()

    with session:
        rows = (
            session.execute(
                select(
                    BookingsTable.id,
                    BookingsTable.booking_time,
                    BookingsTable.status,
                    VehiclesTable.plate_number,
                )
                .join(VehiclesTable, VehiclesTable.id == BookingsTable.vehicle_id)
                .where(
                    and_(
                        BookingsTable.employee_id == emp.id,
                        BookingsTable.booking_date == today,
                    )
                )
                .order_by(BookingsTable.booking_time.asc(), BookingsTable.id.asc())
            )
        ).all()

    if not rows:
        await message.answer(
            "📅 <b>Bugungi bronlar</b>\n\n"
            "Bugun sizga biriktirilgan bronlar yo‘q 😊",
            reply_markup=staff_menu_kb(),
            parse_mode="HTML",
        )
        return

    status_map = {
        "PENDING": "⏳ Kutilmoqda",
        "CONFIRMED": "✅ Tasdiqlandi",
        "IN_PROGRESS": "🛠 Jarayonda",
        "COMPLETED": "🏁 Bajarildi",
        "CANCELLED": "❌ Bekor",
    }

    lines = []
    for b_id, b_time, status, plate in rows:
        t = b_time.strftime("%H:%M") if b_time else "—"
        st = status_map.get(status, status)
        lines.append(f"• <b>{t}</b> — <b>#{b_id}</b> — 🚗 <b>{plate}</b> — {st}")

    await message.answer(
        "📅 <b>Bugungi bronlar</b>\n\n" + "\n".join(lines),
        reply_markup=staff_menu_kb(),
        parse_mode="HTML",
    )


# =========================
# STAFF: MY WORKS (current month list)
# =========================
@router.message(F.text == BTN_WORKS)
@create_session
async def staff_my_works(message: Message, session: Session):
    emp = await get_employee_or_deny(message, session)
    if not emp:
        return

    now = local_now()
    year, month = now.year, now.month

    # repository bor, lekin o'zi session sync -> await bilan chaqiramiz
    wrs = await WorkRecordsRepository.alist_by_employee_month(employee_id=emp.id, year=year, month=month, session=session)

    if not wrs:
        await message.answer(
            "🧾 <b>Mening ishlarim</b>\n\n"
            f"📅 <b>{year}-{month:02d}</b> oyida hozircha ish yozuvlari yo‘q.",
            reply_markup=staff_menu_kb(),
            parse_mode="HTML",
        )
        return

    total_works = Decimal("0")
    total_kpi = Decimal("0")

    lines = []
    for wr in wrs[:20]:
        dt = wr.performed_at.strftime("%d.%m %H:%M") if wr.performed_at else "—"
        total_works += Decimal(str(wr.amount or 0))
        total_kpi += Decimal(str(wr.kpi_amount or 0))
        lines.append(
            f"• <b>{dt}</b> — 💰 <b>{format_money(wr.amount)}</b> so‘m, 🎯 <b>{format_money(wr.kpi_amount)}</b> so‘m"
        )

    await message.answer(
        "🧾 <b>Mening ishlarim</b>\n\n"
        f"📅 <b>Davr:</b> {year}-{month:02d}\n"
        f"🧮 <b>Jami ishlar:</b> <b>{format_money(total_works)}</b> so‘m\n"
        f"🎯 <b>Jami KPI:</b> <b>{format_money(total_kpi)}</b> so‘m\n\n"
        "📌 <b>Oxirgi yozuvlar (20 ta):</b>\n"
        + "\n".join(lines),
        reply_markup=staff_menu_kb(),
        parse_mode="HTML",
    )