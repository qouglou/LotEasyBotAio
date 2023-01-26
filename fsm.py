from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class FSM(StatesGroup):
    requisites = State()
    other_sum = State()
