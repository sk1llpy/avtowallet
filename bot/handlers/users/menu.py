# bot/handlers/users/menu.py
from __future__ import annotations

import datetime
from decimal import Decimal, InvalidOperation
from typing import Iterable

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from sqlalchemy import select, and_, or_, func, delete
from sqlalchemy import union, distinct
from sqlalchemy.orm import Session

from bot.decorators import create_session
from bot.routers import users as router
from bot.keyboards.default import menu as menu_kb

from db.repository import UsersRepository, VehiclesRepository

from db.schemas.users import UsersTable, EmployeesTable
from db.schemas.vehicles import VehiclesTable, BrandsTable, CarModelsTable
from db.schemas.bookings import BookingsTable, BookingServicesTable
from db.schemas.services import (
    ServicesTable,
    ServiceScope,  # TextChoices-like enum/string; if sizda yo‘q bo‘lsa -> o‘chirib tashlang va scope string bilan ishlaydi
    services_service_allowed_brands,
    services_service_allowed_models,
)
from db.schemas.payroll import SalaryProfilesTable, WorkRecordsTable, PayrollMonthsTable


# =========================
# SETTINGS
# =========================
ADMINS_CHAT_ID = -1003898804487  # admin group/supergroup id
TZ_OFFSET_HOURS = 5  # Tashkent


# =========================
# BUTTON TEXTS (USER MENU)
# =========================
BTN_SERVICES = "🚗 Xizmatlarni ko‘rish"
BTN_MY_CARS = "🚘 Mening avtomobillarim"
BTN_BOOK = "📅 Navbatga yozilish"
BTN_MY_ORDERS = "🛠 Mening buyurtmalarim"
BTN_HISTORY = "📜 Tarix"
BTN_LOCATION = "📍 Lokatsiya"
BTN_CONTACT = "📞 Kontakt"
BTN_FEEDBACK = "💬 Murojaat yuborish"
BTN_ADD_CAR = "➕ Avtomobil qo‘shish"


# =========================
# FSM STATES
# =========================
class AddCarState(StatesGroup):
    plate = State()
    brand = State()
    model = State()


class BookingState(StatesGroup):
    vehicle = State()
    date = State()
    time = State()
    confirm = State()


class AdminBookingState(StatesGroup):
    selecting_services = State()
    confirming_total = State()
    custom_total = State()


# =========================
# DATE / TIME HELPERS
# =========================
UZ_MONTHS = {
    1: "yanvar",
    2: "fevral",
    3: "mart",
    4: "aprel",
    5: "may",
    6: "iyun",
    7: "iyul",
    8: "avgust",
    9: "sentyabr",
    10: "oktyabr",
    11: "noyabr",
    12: "dekabr",
}


def now_local() -> datetime.datetime:
    return datetime.datetime.utcnow() + datetime.timedelta(hours=TZ_OFFSET_HOURS)


def today_local() -> datetime.date:
    return now_local().date()


def uz_date_label(d: datetime.date) -> str:
    return f"{d.day}-{UZ_MONTHS[d.month]}"


def normalize_plate(s: str) -> str:
    return (s or "").strip().upper().replace(" ", "")


def money(x: Decimal | int | float | None) -> str:
    if x is None:
        return "0"
    try:
        v = Decimal(str(x))
    except Exception:
        return str(x)
    s = f"{v:.0f}"
    parts = []
    while s:
        parts.append(s[-3:])
        s = s[:-3]
    return " ".join(reversed(parts))


def ikb(rows: list[list[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=rows)


# =========================
# COMMON AUTH HELPERS
# =========================
async def ensure_user(message: Message, session: Session) -> UsersTable | None:
    tg_id = str(message.from_user.id)
    user = UsersRepository.get("tg_id", tg_id, session)
    if not user:
        await message.answer(
            "⚠️ <b>Siz ro‘yxatdan o‘tmagansiz.</b>\n\n/start ni bosing.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML",
        )
        return None
    return user


def get_employee_by_tg_id(tg_id: str, session: Session) -> EmployeesTable | None:
    """
    Telegram user -> UsersTable -> EmployeesTable
    """
    u = session.execute(select(UsersTable).where(UsersTable.tg_id == tg_id)).scalar()
    if not u:
        return None
    emp = session.execute(select(EmployeesTable).where(EmployeesTable.user_id == u.id)).scalar()
    return emp


# =========================
# INLINE KEYBOARDS (USER)
# =========================
def vehicles_ikb(vehicles: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    # [(vehicle_id, label)]
    rows: list[list[InlineKeyboardButton]] = []
    for vid, label in vehicles:
        rows.append([InlineKeyboardButton(text=f"🚘 {label}", callback_data=f"bk:veh:{vid}")])
    rows.append([InlineKeyboardButton(text="➕ Avtomobil qo‘shish", callback_data="bk:add_car")])
    rows.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="bk:cancel")])
    return ikb(rows)


def chunk_buttons(buttons: list[InlineKeyboardButton], size: int = 2):
    rows = []
    for i in range(0, len(buttons), size):
        rows.append(buttons[i:i + size])
    return rows


def brands_ikb(brands: list[BrandsTable]) -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(
            text=f"🏷 {b.name}",
            callback_data=f"car:brand:{b.id}"
        )
        for b in brands[:60]
    ]

    rows = chunk_buttons(buttons, 2)

    # Bekor qilish har doim alohida qatorda
    rows.append([
        InlineKeyboardButton(text="❌ Bekor", callback_data="car:cancel")
    ])

    return ikb(rows)


def models_ikb(models: list[CarModelsTable]) -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(
            text=f"🚘 {m.name}",
            callback_data=f"car:model:{m.id}"
        )
        for m in models[:80]
    ]

    rows = chunk_buttons(buttons, 2)

    rows.append([
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data="car:brand_back")
    ])
    rows.append([
        InlineKeyboardButton(text="❌ Bekor", callback_data="car:cancel")
    ])

    return ikb(rows)

def dates_ikb(dates: list[datetime.date]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(dates), 2):
        chunk = dates[i : i + 2]
        rows.append(
            [
                InlineKeyboardButton(text=f"📅 {uz_date_label(d)}", callback_data=f"bk:date:{d.isoformat()}")
                for d in chunk
            ]
        )
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="bk:back_vehicle")])
    rows.append([InlineKeyboardButton(text="❌ Bekor", callback_data="bk:cancel")])
    return ikb(rows)


def times_ikb(times_: list[str]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(times_), 3):
        chunk = times_[i : i + 3]
        rows.append([InlineKeyboardButton(text=t, callback_data=f"bk:time:{t}") for t in chunk])
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="bk:back_date")])
    rows.append([InlineKeyboardButton(text="❌ Bekor", callback_data="bk:cancel")])
    return ikb(rows)


def confirm_ikb() -> InlineKeyboardMarkup:
    return ikb(
        [
            [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="bk:confirm")],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="bk:back_time")],
            [InlineKeyboardButton(text="❌ Bekor", callback_data="bk:cancel")],
        ]
    )


# =========================
# INLINE KEYBOARDS (ADMIN GROUP)
# =========================
def admin_arrival_ikb(booking_id: int) -> InlineKeyboardMarkup:
    return ikb(
        [
            [
                InlineKeyboardButton(text="✅ Avtomobil keldi", callback_data=f"adm:arr:{booking_id}"),
                InlineKeyboardButton(text="❌ Kelmadi", callback_data=f"adm:narr:{booking_id}"),
            ],
        ]
    )


def admin_services_ikb(
    booking_id: int,
    services: list[ServicesTable],
    selected_ids: set[int],
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []

    for s in services:
        mark = "✅" if s.id in selected_ids else "☑️"
        title = (s.title or "").strip()
        price = money(s.price)
        rows.append([InlineKeyboardButton(text=f"{mark} {title} — {price} so‘m", callback_data=f"adm:svc:{booking_id}:{s.id}")])

    rows.append([InlineKeyboardButton(text="🏁 Yakunlash", callback_data=f"adm:finish:{booking_id}")])
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"adm:back_arr:{booking_id}")])
    rows.append([InlineKeyboardButton(text="❌ Bekor", callback_data=f"adm:cancel:{booking_id}")])
    return ikb(rows)


def admin_total_confirm_ikb(booking_id: int) -> InlineKeyboardMarkup:
    return ikb(
        [
            [InlineKeyboardButton(text="✅ Summani tasdiqlash", callback_data=f"adm:total_ok:{booking_id}")],
            [InlineKeyboardButton(text="✏️ Summani o‘zgartirish", callback_data=f"adm:total_edit:{booking_id}")],
            [InlineKeyboardButton(text="⬅️ Xizmatlarga qaytish", callback_data=f"adm:back_svc:{booking_id}")],
            [InlineKeyboardButton(text="❌ Bekor", callback_data=f"adm:cancel:{booking_id}")],
        ]
    )


# =========================
# DB HELPERS (BOOKING + SERVICES)
# =========================
def booking_is_active(b: BookingsTable) -> bool:
    return (b.status or "").upper() not in ("CANCELLED", "COMPLETED")


def fetch_vehicle_full(vehicle_id: int, session: Session) -> tuple[VehiclesTable, str]:
    """
    returns (vehicle, label: '01A777AA | Chevrolet Cobalt')
    """
    row = session.execute(
        select(VehiclesTable, BrandsTable.name, CarModelsTable.name)
        .join(BrandsTable, BrandsTable.id == VehiclesTable.brand_id)
        .join(CarModelsTable, CarModelsTable.id == VehiclesTable.car_model_id)
        .where(VehiclesTable.id == vehicle_id)
    ).first()
    v, brand_name, model_name = row
    label = f"{v.plate_number} | {brand_name} {model_name}"
    return v, label


def list_user_vehicles(user_id: int, session: Session) -> list[tuple[int, str]]:
    rows = session.execute(
        select(VehiclesTable.id, VehiclesTable.plate_number, BrandsTable.name, CarModelsTable.name)
        .join(BrandsTable, BrandsTable.id == VehiclesTable.brand_id)
        .join(CarModelsTable, CarModelsTable.id == VehiclesTable.car_model_id)
        .where(VehiclesTable.owner_id == user_id)
        .order_by(VehiclesTable.id.desc())
    ).all()
    return [(vid, f"{plate} | {bname} {mname}") for vid, plate, bname, mname in rows]


def list_booked_times(chosen_date: datetime.date, session: Session) -> set[str]:
    rows = session.execute(
        select(BookingsTable.booking_time).where(
            and_(
                BookingsTable.booking_date == chosen_date,
                BookingsTable.status != "CANCELLED",
            )
        )
    ).scalars().all()
    return {t.strftime("%H:%M") for t in rows if t}


def get_allowed_services_for_vehicle(vehicle: VehiclesTable, session: Session) -> list[ServicesTable]:
    """
    scope == ALL => always
    scope == LIMITED => allowed_models includes vehicle.car_model_id OR allowed_brands includes vehicle.brand_id

    ✅ Postgres-safe:
    - UNION removes duplicates automatically
    - no DISTINCT ON => no ORDER BY restriction
    """
    q_all = select(ServicesTable).where(ServicesTable.scope == "ALL")

    q_m = (
        select(ServicesTable)
        .join(
            services_service_allowed_models,
            services_service_allowed_models.c.service_id == ServicesTable.id,
        )
        .where(
            and_(
                ServicesTable.scope == "LIMITED",
                services_service_allowed_models.c.carmodel_id == vehicle.car_model_id,
            )
        )
    )

    q_b = (
        select(ServicesTable)
        .join(
            services_service_allowed_brands,
            services_service_allowed_brands.c.service_id == ServicesTable.id,
        )
        .where(
            and_(
                ServicesTable.scope == "LIMITED",
                services_service_allowed_brands.c.brand_id == vehicle.brand_id,
            )
        )
    )

    u = union(q_all, q_m, q_b).subquery()

    services = (
        session.execute(
            select(ServicesTable)
            .join(u, u.c.id == ServicesTable.id)
            .order_by(ServicesTable.title)
        )
        .scalars()
        .all()
    )
    return services


def upsert_payroll_month(employee_id: int, year: int, month: int, session: Session) -> PayrollMonthsTable:
    pm = session.execute(
        select(PayrollMonthsTable).where(
            and_(
                PayrollMonthsTable.employee_id == employee_id,
                PayrollMonthsTable.year == year,
                PayrollMonthsTable.month == month,
            )
        )
    ).scalar()

    if pm:
        return pm

    pm = PayrollMonthsTable(
        employee_id=employee_id,
        year=year,
        month=month,
        fixed_salary_snapshot=Decimal("0"),
        works_total=Decimal("0"),
        kpi_total=Decimal("0"),
        total_salary=Decimal("0"),
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
        is_active=True,
    )
    session.add(pm)
    session.commit()
    session.refresh(pm)
    return pm


def recalc_payroll_month(employee_id: int, year: int, month: int, session: Session) -> None:
    pm = upsert_payroll_month(employee_id, year, month, session)

    sp = session.execute(select(SalaryProfilesTable).where(SalaryProfilesTable.employee_id == employee_id)).scalar()
    fixed = Decimal(str(sp.fixed_salary)) if sp else Decimal("0")

    rows = session.execute(
        select(WorkRecordsTable.amount, WorkRecordsTable.kpi_amount).where(
            and_(
                WorkRecordsTable.employee_id == employee_id,
                func.extract("year", WorkRecordsTable.performed_at) == year,
                func.extract("month", WorkRecordsTable.performed_at) == month,
            )
        )
    ).all()

    works_total = Decimal("0")
    kpi_total = Decimal("0")
    for a, k in rows:
        works_total += Decimal(str(a or 0))
        kpi_total += Decimal(str(k or 0))

    pm.fixed_salary_snapshot = fixed
    pm.works_total = works_total
    pm.kpi_total = kpi_total
    pm.total_salary = fixed + kpi_total
    pm.updated_at = datetime.datetime.utcnow()
    session.add(pm)
    session.commit()


# =========================
# USER MENU HANDLERS
# =========================
@router.message(F.text == BTN_SERVICES)
@create_session
async def show_services(message: Message, session: Session):
    user = await ensure_user(message, session)
    if not user:
        return
    kb = await menu_kb.button()
    await message.answer(
        "🚗 <b>Xizmatlar</b>\n\n"
        "Bu bo‘limni keyin to‘liq qilamiz ✅\n"
        "Hozircha navbatga yozilish ishlaydi.",
        reply_markup=kb,
        parse_mode="HTML",
    )


@router.message(F.text == BTN_MY_CARS)
@create_session
async def my_cars(message: Message, state: FSMContext, session: Session):
    user = await ensure_user(message, session)
    if not user:
        return

    kb = await menu_kb.button()
    with session:
        vehicles = list_user_vehicles(user.id, session)

    if not vehicles:
        await message.answer(
            "🚘 <b>Mening avtomobillarim</b>\n\n"
            "Sizda hozircha avtomobil yo‘q.\n\n"
            "➕ Avtomobil qo‘shish uchun raqam yuboring 👇\n"
            "Masalan: <i>01A777AA</i>",
            reply_markup=kb,
            parse_mode="HTML",
        )
        await state.clear()
        await state.set_state(AddCarState.plate)
        return

    lines = [f"• <b>{label}</b>" for _, label in vehicles]
    await message.answer(
        "🚘 <b>Mening avtomobillarim</b>\n\n" + "\n".join(lines) + "\n\n"
        "➕ Yangi avtomobil qo‘shish uchun: <b>➕ Avtomobil qo‘shish</b> tugmasini bosing.",
        reply_markup=kb,
        parse_mode="HTML",
    )


@router.message(F.text == BTN_ADD_CAR)
@create_session
async def start_add_car(message: Message, state: FSMContext, session: Session):
    user = await ensure_user(message, session)
    if not user:
        return
    await state.clear()
    await state.set_state(AddCarState.plate)
    await message.answer(
        "➕ <b>Avtomobil qo‘shish</b>\n\n"
        "Davlat raqamini yuboring:\n"
        "Masalan: <i>01A777AA</i>",
        parse_mode="HTML",
    )


@router.message(AddCarState.plate, F.text)
@create_session
async def add_car_plate(message: Message, state: FSMContext, session: Session):
    user = await ensure_user(message, session)
    if not user:
        return

    plate = normalize_plate(message.text)
    if len(plate) < 5:
        await message.answer("❌ Raqam noto‘g‘ri. Masalan: <i>01A777AA</i>", parse_mode="HTML")
        return

    await state.update_data(plate_number=plate)

    with session:
        brands = session.execute(select(BrandsTable).order_by(BrandsTable.name)).scalars().all()

    if not brands:
        await message.answer("❌ Brendlar bazada yo‘q. Admin paneldan brendlarni kiriting.", parse_mode="HTML")
        await state.clear()
        return

    await state.set_state(AddCarState.brand)
    await message.answer("🏷 <b>Brendni tanlang</b> 👇", reply_markup=brands_ikb(brands), parse_mode="HTML")


@router.callback_query(AddCarState.brand, F.data.startswith("car:brand:"))
@create_session
async def add_car_brand(call: CallbackQuery, state: FSMContext, session: Session):
    brand_id = int(call.data.split(":")[-1])
    await state.update_data(brand_id=brand_id)

    with session:
        models = session.execute(
            select(CarModelsTable).where(CarModelsTable.brand_id == brand_id).order_by(CarModelsTable.name)
        ).scalars().all()

    if not models:
        await call.message.answer("❌ Bu brend uchun model yo‘q. Admin paneldan model kiriting.", parse_mode="HTML")
        await call.answer()
        return

    await state.set_state(AddCarState.model)
    await call.message.edit_text("🚘 <b>Modelni tanlang</b> 👇", reply_markup=models_ikb(models), parse_mode="HTML")
    await call.answer()


@router.callback_query(AddCarState.model, F.data.startswith("car:model:"))
@create_session
async def add_car_model(call: CallbackQuery, state: FSMContext, session: Session):
    u = UsersRepository.get("tg_id", str(call.from_user.id), session)
    if not u:
        await call.answer("Avval /start", show_alert=True)
        return

    model_id = int(call.data.split(":")[-1])
    data = await state.get_data()
    plate = data["plate_number"]
    brand_id = data["brand_id"]

    # upsert vehicle (owner+plate unique)
    vehicle = await VehiclesRepository.aupsert_vehicle(
        owner_id=u.id,
        brand_id=brand_id,
        car_model_id=model_id,
        plate_number=plate,
        year=None,
        color=None,
        session=session,
    )

    await state.clear()
    kb = await menu_kb.button()

    with session:
        _, label = fetch_vehicle_full(vehicle.id, session)

    await call.message.edit_text(
        "✅ <b>Avtomobil qo‘shildi!</b> 🎉\n\n"
        f"🚘 <b>{label}</b>\n\n"
        "Endi menyudan foydalanishingiz mumkin 👇",
        parse_mode="HTML",
    )
    await call.message.answer("🏠 <b>Menyu</b>", reply_markup=kb, parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data.in_(["car:cancel", "car:brand_back"]))
@create_session
async def add_car_cancel_generic(call: CallbackQuery, state: FSMContext, session: Session):
    await state.clear()
    kb = await menu_kb.button()
    await call.message.edit_text("❌ Bekor qilindi.", parse_mode="HTML")
    await call.message.answer("🏠 <b>Menyu</b>", reply_markup=kb, parse_mode="HTML")
    await call.answer()


# =========================
# BOOKING FLOW (USER)
# =========================
@router.message(F.text == BTN_BOOK)
@create_session
async def booking_start(message: Message, state: FSMContext, session: Session):
    user = await ensure_user(message, session)
    if not user:
        return

    await state.clear()

    with session:
        vehicles = list_user_vehicles(user.id, session)

    if not vehicles:
        await state.set_state(AddCarState.plate)
        kb = await menu_kb.button()
        await message.answer(
            "📅 <b>Navbatga yozilish</b>\n\n"
            "Avval avtomobil qo‘shish kerak 🚘\n\n"
            "Davlat raqamini yuboring:\n"
            "Masalan: <i>01A777AA</i>",
            reply_markup=kb,
            parse_mode="HTML",
        )
        return

    await state.set_state(BookingState.vehicle)
    await message.answer(
        "📅 <b>Navbatga yozilish</b>\n\n"
        "1) Avtomobilni tanlang 👇",
        reply_markup=vehicles_ikb(vehicles),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "bk:cancel")
@create_session
async def booking_cancel_any(call: CallbackQuery, state: FSMContext, session: Session):
    await state.clear()
    kb = await menu_kb.button()
    await call.message.edit_text("❌ Bekor qilindi.", parse_mode="HTML")
    await call.message.answer("🏠 <b>Menyu</b>", reply_markup=kb, parse_mode="HTML")
    await call.answer()


@router.callback_query(BookingState.vehicle, F.data.startswith("bk:veh:"))
@create_session
async def booking_choose_vehicle(call: CallbackQuery, state: FSMContext, session: Session):
    vehicle_id = int(call.data.split(":")[-1])
    await state.update_data(vehicle_id=vehicle_id)

    start = today_local()
    dates = [start + datetime.timedelta(days=i) for i in range(15)]

    await state.set_state(BookingState.date)
    await call.message.edit_text(
        "📅 <b>2) Sanani tanlang</b> 👇\n\n"
        "⏳ 15 kun ichidan tanlaysiz:",
        reply_markup=dates_ikb(dates),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(BookingState.vehicle, F.data == "bk:add_car")
@create_session
async def booking_add_car_from_vehicle(call: CallbackQuery, state: FSMContext, session: Session):
    await state.clear()
    await state.set_state(AddCarState.plate)
    await call.message.edit_text(
        "➕ <b>Avtomobil qo‘shish</b>\n\n"
        "Davlat raqamini yuboring:\n"
        "Masalan: <i>01A777AA</i>",
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(BookingState.date, F.data == "bk:back_vehicle")
@create_session
async def booking_back_to_vehicle(call: CallbackQuery, state: FSMContext, session: Session):
    u = UsersRepository.get("tg_id", str(call.from_user.id), session)
    if not u:
        await call.answer("Avval /start", show_alert=True)
        return

    with session:
        vehicles = list_user_vehicles(u.id, session)

    await state.set_state(BookingState.vehicle)
    await call.message.edit_text(
        "📅 <b>1) Avtomobilni tanlang</b> 👇",
        reply_markup=vehicles_ikb(vehicles),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(BookingState.date, F.data.startswith("bk:date:"))
@create_session
async def booking_choose_date(call: CallbackQuery, state: FSMContext, session: Session):
    chosen_date = datetime.date.fromisoformat(call.data.split(":")[-1])

    all_times = [f"{h:02d}:{m:02d}" for h in range(10, 19) for m in (0, 30)]
    with session:
        booked = list_booked_times(chosen_date, session)
    available = [t for t in all_times if t not in booked]

    if not available:
        await call.answer()
        await call.message.answer("😕 <b>Bu kunda bo‘sh vaqt qolmagan.</b>\n\nBoshqa sanani tanlang ✅", parse_mode="HTML")
        return

    await state.update_data(date=chosen_date.isoformat())
    await state.set_state(BookingState.time)

    await call.message.edit_text(
        "⏰ <b>3) Vaqtni tanlang</b> 👇\n\n"
        f"📅 Sana: <b>{uz_date_label(chosen_date)}</b>",
        reply_markup=times_ikb(available),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(BookingState.time, F.data == "bk:back_date")
@create_session
async def booking_back_to_date(call: CallbackQuery, state: FSMContext, session: Session):
    start = today_local()
    dates = [start + datetime.timedelta(days=i) for i in range(10)]
    await state.set_state(BookingState.date)
    await call.message.edit_text("📅 <b>2) Sanani tanlang</b> 👇", reply_markup=dates_ikb(dates), parse_mode="HTML")
    await call.answer()


@router.callback_query(BookingState.time, F.data.startswith("bk:time:"))
@create_session
async def booking_choose_time(call: CallbackQuery, state: FSMContext, session: Session):
    time_str_h = call.data.split(":")[-2]  # "10:00"
    time_str_m = call.data.split(":")[-1]  # "10:00"
    time_str = f"{time_str_h}:{time_str_m}"
    await state.update_data(time=time_str)

    data = await state.get_data()
    chosen_date = datetime.date.fromisoformat(data["date"])
    chosen_time = datetime.time.fromisoformat(time_str)

    # race check
    with session:
        exists = session.execute(
            select(BookingsTable.id).where(
                and_(
                    BookingsTable.booking_date == chosen_date,
                    BookingsTable.booking_time == chosen_time,
                    BookingsTable.status != "CANCELLED",
                )
            )
        ).scalar()

    if exists:
        await call.answer("Bu vaqt band bo‘lib qoldi. Boshqasini tanlang.", show_alert=True)
        return

    await state.set_state(BookingState.confirm)
    await call.message.edit_text(
        "✅ <b>4) Tasdiqlash</b>\n\n"
        f"📅 Sana: <b>{uz_date_label(chosen_date)}</b>\n"
        f"⏰ Vaqt: <b>{time_str}</b>\n\n"
        "Tasdiqlaysizmi? 👇",
        reply_markup=confirm_ikb(),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(BookingState.confirm, F.data == "bk:back_time")
@create_session
async def booking_back_to_time(call: CallbackQuery, state: FSMContext, session: Session):
    data = await state.get_data()
    chosen_date = datetime.date.fromisoformat(data["date"])

    all_times = [f"{h:02d}:00" for h in range(10, 19)]
    with session:
        booked = list_booked_times(chosen_date, session)
    available = [t for t in all_times if t not in booked]

    await state.set_state(BookingState.time)
    await call.message.edit_text(
        "⏰ <b>3) Vaqtni tanlang</b> 👇\n\n"
        f"📅 Sana: <b>{uz_date_label(chosen_date)}</b>",
        reply_markup=times_ikb(available),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(BookingState.confirm, F.data == "bk:confirm")
@create_session
async def booking_confirm(call: CallbackQuery, state: FSMContext, session: Session):
    u = UsersRepository.get("tg_id", str(call.from_user.id), session)
    if not u:
        await call.answer("Avval /start", show_alert=True)
        return

    data = await state.get_data()
    vehicle_id = int(data["vehicle_id"])
    chosen_date = datetime.date.fromisoformat(data["date"])
    chosen_time = datetime.time.fromisoformat(data["time"])

    # final lock check
    with session:
        exists = session.execute(
            select(BookingsTable.id).where(
                and_(
                    BookingsTable.booking_date == chosen_date,
                    BookingsTable.booking_time == chosen_time,
                    BookingsTable.status != "CANCELLED",
                )
            )
        ).scalar()

    if exists:
        await state.clear()
        kb = await menu_kb.button()
        await call.message.edit_text("❌ <b>Vaqt band bo‘lib qoldi.</b>\n\nQayta yoziling.", parse_mode="HTML")
        await call.message.answer("🏠 <b>Menyu</b>", reply_markup=kb, parse_mode="HTML")
        await call.answer("Band ❌", show_alert=True)
        return

    # create booking
    with session:
        booking = BookingsTable(
            client_id=u.id,
            vehicle_id=vehicle_id,
            booking_date=chosen_date,
            booking_time=chosen_time,
            status="PENDING",
            employee_id=None,
            note=None,
            total_amount=None,
            completed_at=None,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
            is_active=True,
        )
        session.add(booking)
        session.commit()
        session.refresh(booking)

        vehicle, v_label = fetch_vehicle_full(vehicle_id, session)

    # send to admin group with arrival buttons
    try:
        client_name = (u.tg_full_name or f"{u.first_name or ''} {u.last_name or ''}".strip() or u.tg_id).strip()
        phone = u.phone_number or "—"
        await call.bot.send_message(
            chat_id=ADMINS_CHAT_ID,
            text=(
                "🆕 <b>Yangi bron</b>\n\n"
                f"🆔 <b>Bron:</b> <b>#{booking.id}</b>\n"
                f"👤 <b>Mijoz:</b> {client_name}\n"
                f"📞 <b>Telefon:</b> <b>{phone}</b>\n"
                f"🚘 <b>Avtomobil:</b> <b>{v_label}</b>\n"
                f"📅 <b>Sana:</b> <b>{uz_date_label(chosen_date)}</b>\n"
                f"⏰ <b>Vaqt:</b> <b>{chosen_time.strftime('%H:%M')}</b>\n\n"
                "Ijrochi, holatni belgilang 👇"
            ),
            reply_markup=admin_arrival_ikb(booking.id),
            parse_mode="HTML",
        )
    except Exception:
        # groupga yuborilmasa ham user booking saqlanib qoladi
        pass

    await state.clear()
    kb = await menu_kb.button()
    await call.message.edit_text(
        "🎉 <b>Bron tasdiqlandi!</b> ✅\n\n"
        f"🆔 Bron: <b>#{booking.id}</b>\n"
        f"📅 Sana: <b>{uz_date_label(chosen_date)}</b>\n"
        f"⏰ Vaqt: <b>{chosen_time.strftime('%H:%M')}</b>\n\n"
        "Tez orada operator/usta tasdiqlaydi 📞",
        parse_mode="HTML",
    )
    await call.message.answer("🏠 <b>Menyu</b>", reply_markup=kb, parse_mode="HTML")
    await call.answer("Tayyor ✅", show_alert=False)


# =========================
# ORDERS / HISTORY / CONTACT
# =========================
@router.message(F.text == BTN_MY_ORDERS)
@create_session
async def my_orders(message: Message, session: Session):
    u = await ensure_user(message, session)
    if not u:
        return

    kb = await menu_kb.button()
    with session:
        rows = session.execute(
            select(BookingsTable)
            .where(BookingsTable.client_id == u.id)
            .order_by(BookingsTable.booking_date.desc(), BookingsTable.booking_time.desc(), BookingsTable.id.desc())
            .limit(15)
        ).scalars().all()

    if not rows:
        await message.answer("🛠 <b>Mening buyurtmalarim</b>\n\nSizda hozircha buyurtmalar yo‘q.", reply_markup=kb, parse_mode="HTML")
        return

    status_map = {
        "PENDING": "⏳ Kutilmoqda",
        "CONFIRMED": "✅ Tasdiqlandi",
        "IN_PROGRESS": "🛠 Jarayonda",
        "COMPLETED": "🏁 Bajarildi",
        "CANCELLED": "❌ Bekor",
    }

    lines = []
    for b in rows:
        d_txt = b.booking_date.strftime("%d.%m.%Y") if b.booking_date else "—"
        t_txt = b.booking_time.strftime("%H:%M") if b.booking_time else "—"
        st = status_map.get((b.status or "").upper(), b.status or "—")
        total = money(b.total_amount) if b.total_amount is not None else "—"
        lines.append(f"• <b>#{b.id}</b> — {st} — 🗓 {d_txt} {t_txt} — 💰 <b>{total}</b> so‘m")

    await message.answer("🛠 <b>Mening buyurtmalarim</b>\n\n" + "\n".join(lines), reply_markup=kb, parse_mode="HTML")


@router.message(F.text == BTN_HISTORY)
@create_session
async def history(message: Message, session: Session):
    u = await ensure_user(message, session)
    if not u:
        return
    kb = await menu_kb.button()

    with session:
        completed = session.execute(
            select(func.count()).select_from(BookingsTable).where(and_(BookingsTable.client_id == u.id, BookingsTable.status == "COMPLETED"))
        ).scalar() or 0
        cancelled = session.execute(
            select(func.count()).select_from(BookingsTable).where(and_(BookingsTable.client_id == u.id, BookingsTable.status == "CANCELLED"))
        ).scalar() or 0
        total = session.execute(
            select(func.count()).select_from(BookingsTable).where(BookingsTable.client_id == u.id)
        ).scalar() or 0

    await message.answer(
        "📜 <b>Tarix</b>\n\n"
        f"🏁 Bajarilgan: <b>{completed}</b>\n"
        f"❌ Bekor qilingan: <b>{cancelled}</b>\n"
        f"📦 Jami: <b>{total}</b>",
        reply_markup=kb,
        parse_mode="HTML",
    )


@router.message(F.text == BTN_LOCATION)
async def location(message: Message):
    kb = await menu_kb.button()
    await message.answer_location(latitude=41.321716,longitude=69.202454)
    await message.answer(
        "📍 <b>Lokatsiya</b>\n\n"
        "📌 Mannon-uyg'ur 38.\n",
        reply_markup=kb,
        parse_mode="HTML",
    )


@router.message(F.text == BTN_CONTACT)
async def contact(message: Message):
    kb = await menu_kb.button()
    await message.answer(
        "📞 <b>Kontakt</b>\n\n"
        "☎️ Telefon: <b>+998 97-773-88-85</b>\n"
        "💬 Telegram: <b>@avto_walllet</b>",
        reply_markup=kb,
        parse_mode="HTML",
    )


@router.message(F.text == BTN_FEEDBACK)
async def feedback(message: Message):
    kb = await menu_kb.button()
    await message.answer(
        "💬 <b>Murojaat yuborish</b>\n\n"
        "📝 Muammo yoki taklifingizni shu yerga yozib yuboring.\n"
        "Keyin men uni adminlarga yuboraman ✅",
        reply_markup=kb,
        parse_mode="HTML",
    )


# =========================
# ADMIN GROUP FLOW (ARRIVAL -> SERVICES -> FINISH -> TOTAL EDIT -> COMPLETE)
# =========================
@router.callback_query(F.data.startswith("adm:arr:"))
@create_session
async def admin_mark_arrived(call: CallbackQuery, state: FSMContext, session: Session):
    booking_id = int(call.data.split(":")[-1])

    # only employees can do this
    with session:
        emp = get_employee_by_tg_id(str(call.from_user.id), session)
        if not emp:
            await call.answer("Siz ijrochi emassiz.", show_alert=True)
            return

        b = session.execute(select(BookingsTable).where(BookingsTable.id == booking_id)).scalar()
        if not b:
            await call.answer("Bron topilmadi.", show_alert=True)
            return
        if not booking_is_active(b):
            await call.answer("Bron allaqachon yakunlangan/bekor qilingan.", show_alert=True)
            return

        # assign employee + IN_PROGRESS
        b.employee_id = emp.id
        b.status = "IN_PROGRESS"
        b.updated_at = datetime.datetime.utcnow()
        session.add(b)
        session.commit()

        vehicle = session.execute(select(VehiclesTable).where(VehiclesTable.id == b.vehicle_id)).scalar()
        services = get_allowed_services_for_vehicle(vehicle, session)

    await state.clear()
    await state.set_state(AdminBookingState.selecting_services)
    await state.update_data(booking_id=booking_id, selected_service_ids=[])

    await call.message.edit_text(
        "🛠 <b>Avtomobil keldi ✅</b>\n\n"
        f"🆔 <b>Bron:</b> <b>#{booking_id}</b>\n"
        "Quyidan bajarilgan xizmatlarni tanlang 👇\n\n"
        "☑️ — tanlanmagan, ✅ — tanlangan",
        reply_markup=admin_services_ikb(booking_id, services, set()),
        parse_mode="HTML",
    )
    await call.answer("Keldi ✅")


@router.callback_query(F.data.startswith("adm:narr:"))
@create_session
async def admin_mark_not_arrived(call: CallbackQuery, state: FSMContext, session: Session):
    booking_id = int(call.data.split(":")[-1])

    with session:
        emp = get_employee_by_tg_id(str(call.from_user.id), session)
        if not emp:
            await call.answer("Siz ijrochi emassiz.", show_alert=True)
            return

        b = session.execute(select(BookingsTable).where(BookingsTable.id == booking_id)).scalar()
        if not b:
            await call.answer("Bron topilmadi.", show_alert=True)
            return
        if not booking_is_active(b):
            await call.answer("Bron allaqachon yakunlangan/bekor qilingan.", show_alert=True)
            return

        b.employee_id = emp.id
        b.status = "CANCELLED"
        b.note = "Kelmadi"
        b.updated_at = datetime.datetime.utcnow()
        session.add(b)
        session.commit()

    await state.clear()
    await call.message.edit_text(
        "❌ <b>Bekor qilindi</b>\n\n"
        f"🆔 <b>Bron:</b> <b>#{booking_id}</b>\n"
        "Holat: <b>Kelmadi</b>",
        parse_mode="HTML",
    )
    await call.answer("Kelmadi ❌")


@router.callback_query(F.data.startswith("adm:svc:"))
@create_session
async def admin_toggle_service(call: CallbackQuery, state: FSMContext, session: Session):
    # adm:svc:<booking_id>:<service_id>
    _, _, booking_id_s, service_id_s = call.data.split(":")
    booking_id = int(booking_id_s)
    service_id = int(service_id_s)

    if (await state.get_state()) != AdminBookingState.selecting_services.state:
        await call.answer("Avval 'Avtomobil keldi' ni bosing.", show_alert=True)
        return

    data = await state.get_data()
    if int(data.get("booking_id", 0)) != booking_id:
        await call.answer("Bu panel boshqa bron uchun.", show_alert=True)
        return

    selected = set(map(int, data.get("selected_service_ids", []) or []))
    if service_id in selected:
        selected.remove(service_id)
    else:
        selected.add(service_id)

    with session:
        b = session.execute(select(BookingsTable).where(BookingsTable.id == booking_id)).scalar()
        if not b or not booking_is_active(b):
            await call.answer("Bron aktiv emas.", show_alert=True)
            return

        vehicle = session.execute(select(VehiclesTable).where(VehiclesTable.id == b.vehicle_id)).scalar()
        services = get_allowed_services_for_vehicle(vehicle, session)

    await state.update_data(selected_service_ids=list(selected))

    total = Decimal("0")
    for s in services:
        if s.id in selected:
            total += Decimal(str(s.price or 0))

    await call.message.edit_text(
        "🛠 <b>Xizmat tanlash</b>\n\n"
        f"🆔 <b>Bron:</b> <b>#{booking_id}</b>\n"
        f"🧾 Tanlangan: <b>{len(selected)}</b> ta\n"
        f"💰 Hozirgi summa: <b>{money(total)}</b> so‘m\n\n"
        "☑️ — tanlanmagan, ✅ — tanlangan",
        reply_markup=admin_services_ikb(booking_id, services, selected),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data.startswith("adm:finish:"))
@create_session
async def admin_finish_services(call: CallbackQuery, state: FSMContext, session: Session):
    booking_id = int(call.data.split(":")[-1])

    if (await state.get_state()) != AdminBookingState.selecting_services.state:
        await call.answer("Avval xizmatlarni tanlang.", show_alert=True)
        return

    data = await state.get_data()
    selected = set(map(int, data.get("selected_service_ids", []) or []))
    if not selected:
        await call.answer("Hech qanday xizmat tanlanmadi.", show_alert=True)
        return

    with session:
        b = session.execute(select(BookingsTable).where(BookingsTable.id == booking_id)).scalar()
        if not b or not booking_is_active(b):
            await call.answer("Bron aktiv emas.", show_alert=True)
            return

        vehicle = session.execute(select(VehiclesTable).where(VehiclesTable.id == b.vehicle_id)).scalar()
        allowed_services = get_allowed_services_for_vehicle(vehicle, session)

    total = Decimal("0")
    chosen_services = [s for s in allowed_services if s.id in selected]
    for s in chosen_services:
        total += Decimal(str(s.price or 0))

    await state.set_state(AdminBookingState.confirming_total)
    await state.update_data(total_amount=str(total))

    lines = [f"• {s.title} — <b>{money(s.price)}</b> so‘m" for s in chosen_services]
    await call.message.edit_text(
        "🏁 <b>Yakunlash</b>\n\n"
        f"🆔 <b>Bron:</b> <b>#{booking_id}</b>\n\n"
        "🧾 <b>Tanlangan xizmatlar:</b>\n"
        + "\n".join(lines)
        + "\n\n"
        f"💰 <b>Jami summa:</b> <b>{money(total)}</b> so‘m\n\n"
        "Summani tasdiqlaysizmi? 👇",
        reply_markup=admin_total_confirm_ikb(booking_id),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data.startswith("adm:total_edit:"))
@create_session
async def admin_total_edit(call: CallbackQuery, state: FSMContext, session: Session):
    booking_id = int(call.data.split(":")[-1])

    if (await state.get_state()) != AdminBookingState.confirming_total.state:
        await call.answer("Avval yakunlashga chiqing.", show_alert=True)
        return

    await state.set_state(AdminBookingState.custom_total)
    await call.message.answer(
        "✏️ <b>Summani kiriting</b>\n\n"
        "Faqat raqam yuboring.\n"
        "Masalan: <code>250000</code>",
        parse_mode="HTML",
    )
    await call.answer()


@router.message(AdminBookingState.custom_total, F.text)
@create_session
async def admin_total_receive(message: Message, state: FSMContext, session: Session):
    # This message comes from executor in the same chat (group)
    data = await state.get_data()
    booking_id = int(data.get("booking_id") or 0)
    if not booking_id:
        await state.clear()
        return

    raw = (message.text or "").strip().replace(" ", "").replace(",", ".")
    try:
        val = Decimal(raw)
        if val < 0:
            raise InvalidOperation
    except Exception:
        await message.answer("❌ Noto‘g‘ri summa. Masalan: <code>250000</code>", parse_mode="HTML")
        return

    await state.set_state(AdminBookingState.confirming_total)
    await state.update_data(total_amount=str(val))

    await message.answer(
        "✅ <b>Summa yangilandi</b>\n\n"
        f"💰 Yangi summa: <b>{money(val)}</b> so‘m\n\n"
        "Endi tasdiqlang 👇",
        reply_markup=admin_total_confirm_ikb(booking_id),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("adm:back_svc:"))
@create_session
async def admin_back_to_services(call: CallbackQuery, state: FSMContext, session: Session):
    booking_id = int(call.data.split(":")[-1])

    data = await state.get_data()
    selected = set(map(int, data.get("selected_service_ids", []) or []))

    with session:
        b = session.execute(select(BookingsTable).where(BookingsTable.id == booking_id)).scalar()
        if not b or not booking_is_active(b):
            await call.answer("Bron aktiv emas.", show_alert=True)
            return
        vehicle = session.execute(select(VehiclesTable).where(VehiclesTable.id == b.vehicle_id)).scalar()
        services = get_allowed_services_for_vehicle(vehicle, session)

    await state.set_state(AdminBookingState.selecting_services)
    await call.message.edit_text(
        "🛠 <b>Xizmat tanlash</b>\n\n"
        f"🆔 <b>Bron:</b> <b>#{booking_id}</b>\n\n"
        "☑️ — tanlanmagan, ✅ — tanlangan",
        reply_markup=admin_services_ikb(booking_id, services, selected),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data.startswith("adm:back_arr:"))
@create_session
async def admin_back_to_arrival(call: CallbackQuery, state: FSMContext, session: Session):
    booking_id = int(call.data.split(":")[-1])
    await state.clear()
    await call.message.edit_text(
        "🚗 <b>Holatni tanlang</b>\n\n"
        f"🆔 <b>Bron:</b> <b>#{booking_id}</b>\n"
        "Avtomobil keldimi?",
        reply_markup=admin_arrival_ikb(booking_id),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data.startswith("adm:cancel:"))
@create_session
async def admin_cancel_flow(call: CallbackQuery, state: FSMContext, session: Session):
    booking_id = int(call.data.split(":")[-1])
    await state.clear()
    await call.message.edit_text("❌ Bekor qilindi.", parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data.startswith("adm:total_ok:"))
@create_session
async def admin_complete_booking(call: CallbackQuery, state: FSMContext, session: Session):
    booking_id = int(call.data.split(":")[-1])

    if (await state.get_state()) != AdminBookingState.confirming_total.state:
        await call.answer("Avval yakunlashga chiqing.", show_alert=True)
        return

    data = await state.get_data()
    selected = set(map(int, data.get("selected_service_ids", []) or []))
    if not selected:
        await call.answer("Xizmatlar tanlanmagan.", show_alert=True)
        return

    try:
        total_amount = Decimal(str(data.get("total_amount") or "0"))
    except Exception:
        total_amount = Decimal("0")

    with session:
        emp = get_employee_by_tg_id(str(call.from_user.id), session)
        if not emp:
            await call.answer("Siz ijrochi emassiz.", show_alert=True)
            return

        b = session.execute(select(BookingsTable).where(BookingsTable.id == booking_id)).scalar()
        if not b:
            await call.answer("Bron topilmadi.", show_alert=True)
            return
        if (b.status or "").upper() == "COMPLETED":
            await call.answer("Allaqachon yakunlangan.", show_alert=True)
            return

        # fetch allowed services again and keep only selected
        vehicle = session.execute(select(VehiclesTable).where(VehiclesTable.id == b.vehicle_id)).scalar()
        allowed_services = get_allowed_services_for_vehicle(vehicle, session)
        chosen_services = [s for s in allowed_services if s.id in selected]

        if not chosen_services:
            await call.answer("Tanlangan xizmatlar mos emas.", show_alert=True)
            return

        # 1) clear previous booking services (if any)
        session.execute(delete(BookingServicesTable).where(BookingServicesTable.booking_id == booking_id))

        # 2) insert booking services
        for s in chosen_services:
            bs = BookingServicesTable(
                booking_id=booking_id,
                service_id=s.id,
                price=s.price or Decimal("0"),
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
                is_active=True,
            )
            session.add(bs)

        # 3) set booking completed
        b.employee_id = emp.id
        b.total_amount = total_amount
        b.completed_at = datetime.datetime.utcnow()
        b.status = "COMPLETED"
        b.updated_at = datetime.datetime.utcnow()
        session.add(b)

        # 4) workrecord create/update
        sp = session.execute(select(SalaryProfilesTable).where(SalaryProfilesTable.employee_id == emp.id)).scalar()
        kpi_percent = int(getattr(sp, "kpi_percent", 10) or 10)
        kpi_amount = (Decimal(str(total_amount)) * Decimal(kpi_percent)) / Decimal("100")

        wr = session.execute(select(WorkRecordsTable).where(WorkRecordsTable.booking_id == booking_id)).scalar()
        if wr:
            wr.amount = total_amount
            wr.kpi_percent = kpi_percent
            wr.kpi_amount = kpi_amount
            wr.performed_at = datetime.datetime.utcnow()
            wr.updated_at = datetime.datetime.utcnow()
            session.add(wr)
        else:
            wr = WorkRecordsTable(
                employee_id=emp.id,
                booking_id=booking_id,
                amount=total_amount,
                kpi_percent=kpi_percent,
                kpi_amount=kpi_amount,
                performed_at=datetime.datetime.utcnow(),
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
                is_active=True,
            )
            session.add(wr)

        session.commit()

        # 5) payroll month recalc
        dt = now_local()
        recalc_payroll_month(emp.id, dt.year, dt.month, session)

    await state.clear()
    await call.message.edit_text(
        "✅ <b>Ish yakunlandi!</b> 🏁\n\n"
        f"🆔 <b>Bron:</b> <b>#{booking_id}</b>\n"
        f"💰 <b>Jami:</b> <b>{money(total_amount)}</b> so‘m\n"
        f"🎯 <b>KPI:</b> <b>{money((total_amount * Decimal(kpi_percent)) / Decimal('100'))}</b> so‘m",
        parse_mode="HTML",
    )
    await call.answer("Yakunlandi ✅")