from aiogram.fsm.state import State, StatesGroup


class FSM(StatesGroup):
    requisites = State()
    other_sum = State()
    accure_id_trans = State()
    adm_new_requis = State()
    enter_id_user = State()
