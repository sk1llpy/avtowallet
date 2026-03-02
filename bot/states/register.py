from aiogram.fsm.state import State, StatesGroup

class RegisterState(StatesGroup):
    phone_number = State()