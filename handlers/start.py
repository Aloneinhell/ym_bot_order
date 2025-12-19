import os

import dotenv
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select

from data.database import AsyncSessionLocal
from config import bot
from data.models import Admins
from keyboards import inline
from services.utils.get_api_creds import get_cur_cabinet, get_cur_shop


class Form(StatesGroup):
    msg_id = State()
    chat_id = State()


dotenv.load_dotenv()

OWNER1 = os.getenv('OWNER1')
OWNER2 = os.getenv('OWNER2')
DEV = os.getenv('DEV')

STAFF = [OWNER1, OWNER2, DEV, 'pleaks_0', 'portall_23', 'taehyungswifenumber1', 'VladBrightty', 'Natalia251220']


def get_start_router():
    router = Router()

    @router.message(CommandStart())
    async def handle_start(msg: types.Message, state: FSMContext):
        state_data = await state.get_data()
        is_cabinet_setted = False
        is_shop_setted = False
        try:
            is_cabinet_setted = state_data['is_cabinet_setted']
            is_shop_setted = state_data['is_shop_setted']
        except:
            ...
        finally:
            username = msg.from_user.username
            tg_id = msg.from_user.id
            if username in STAFF:
                async with AsyncSessionLocal() as session:
                    existing_admin = await session.scalar(select(Admins).where(Admins.tg_id == tg_id))
                    if not existing_admin:
                        new_admin = Admins(
                            username=username,
                            tg_id=tg_id
                        )
                        session.add(new_admin)
                        await session.commit()
                text = f"Здравствуйте, <b>{msg.from_user.first_name}</b>👋\n\n"
                if is_cabinet_setted and is_shop_setted:
                    cur_cabinet = await get_cur_cabinet()
                    cur_shop = await get_cur_shop()
                    text += f"<blockquote>Кабинет: {cur_cabinet.b_id}\n" \
                            f"Магазин: {cur_shop.c_id} / {cur_shop.domain}" \
                            f"</blockquote>"
                sent_msg = await msg.answer(text=text, reply_markup=inline.menu_kb(is_cabinet_setted=is_cabinet_setted,
                                                                                   is_shop_setted=is_shop_setted),
                                            parse_mode='HTML')
                await state.update_data(msg_id=sent_msg.message_id)
                await state.update_data(chat_id=msg.chat.id)

    return router
