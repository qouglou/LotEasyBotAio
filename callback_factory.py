from typing import Optional
from aiogram.filters.callback_data import CallbackData


class BalanceManageCallback(CallbackData, prefix="balance"):
    action: Optional[str] #choose_way, choose_sum, check_withd, choose_other, bet_other, check_topup, confirm_withd, check_bet,
    # change_bet, create_bet, create_request, enter_requisites, choose_bet, get_statistics
    role: Optional[str] #user, admin
    operation: Optional[str] #topup, withd, bet, rem, add, set
    game: Optional[str] #bowl, cube, slot, duel, russ, king
    way: Optional[str] #qiwi, bank
    sum: Optional[int]
    from_where: Optional[str] #main,
    id_msg: Optional[str]
    id_oper: Optional[str]
    requisites: Optional[str]


class AdminManageCallback(CallbackData, prefix="admin"):
    user_id: Optional[str]
    user_nickname: Optional[str]
    action: Optional[str] #open_main, check_oper, confirm_oper, choose_type, select_oper, change_balance,
    # user_info, oper_info, user_balance, choose_user, check_ban, ban_user, change_way, change_requisites, new_requisites, user_checker, choose_admin, admin_info, admin_list, add_admin
    sum: Optional[int]
    key: Optional[str]
    from_where: Optional[str]
    id_oper: Optional[int]
    operation: Optional[str]
    old_way: Optional[str]
    new_way: Optional[str]
    new_requisites: Optional[str]



