from aiogram.filters import BaseFilter
from aiogram.types import Message


class ForwardedFilter(BaseFilter):
    is_forwarded: bool

    async def __call__(self, message: Message):
        if message.forward_from or message.forward_from_chat or message.forward_sender_name:
            return True
        else:
            return False
