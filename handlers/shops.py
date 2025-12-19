from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update

from config import bot
from data.database import AsyncSessionLocal
from data.models import Shops
from keyboards import inline
from services.utils.get_api_creds import get_cur_shop, get_cur_cabinet


def get_shops_router():
    router = Router()

    @router.callback_query(F.data == 'shops_menu')
    async def handle_shops_menu(callback: types.CallbackQuery, state: FSMContext):
        chat_id = callback.message.chat.id
        msg_id = callback.message.message_id

        cur_shop = await get_cur_shop()
        cur_cabinet = await get_cur_cabinet()
        #b_id = cur_cabinet.b_id
        async with AsyncSessionLocal() as session:
            available_shops_res = await session.scalars(select(Shops))
            available_shops = available_shops_res.all()
            text = f"<b>⛺Список магазинов:\n\n</b>" \
                   f"<blockquote>Текущий магазин: {cur_shop.c_id} - {cur_shop.domain}</blockquote>"
            shops_list = []
            for shop in available_shops:
                if shop.is_chosen:
                    ...
                else:
                    shops_list.append(shop)
            await state.update_data(is_shop_setted=True)
            await state.update_data(is_cabinet_setted=True)
            await bot.edit_message_text(text=text, chat_id=chat_id, message_id=msg_id,
                                        parse_mode='HTML',
                                        reply_markup=inline.shop_switch_kb(shops=shops_list))

    @router.callback_query(F.data == 'no_shops_no_answer')
    async def handle_no_shops_btn(callback: types.CallbackQuery):
        await callback.answer()

    @router.callback_query(F.data.startswith('switch_shop_'))
    async def handle_shop_switch(callback: types.CallbackQuery, state: FSMContext):
        print(f"\n\nYEAH\n\n")
        chat_id = callback.message.chat.id
        msg_id = callback.message.message_id
        c_id_str = callback.data[12:]
        c_id = int(c_id_str)
        print(f"\n\nC_id = {c_id}\n\n")
        async with AsyncSessionLocal() as session:
            cur_shop = await get_cur_shop()
            await session.execute(update(Shops).where(Shops.c_id == cur_shop.c_id).values(
                is_chosen=False
            ))
            await session.commit()
            await session.execute(update(Shops).where(Shops.c_id == c_id).values(
                is_chosen=True
            ))
            await session.commit()
            new_cur_shop = await get_cur_shop()
            text = f"<b>✅Магазин успешно изменен!\n</b>" \
                   f"<blockquote>" \
                   f"⛺Текущий магазин: {new_cur_shop.c_id} - {new_cur_shop.domain}" \
                   f"</blockquote>"
            await bot.edit_message_text(text=text, chat_id=chat_id, message_id=msg_id,
                                        parse_mode='HTML',
                                        reply_markup=inline.back_kb())
            await state.update_data(is_shop_setted=True)
            await state.update_data(is_cabinet_setted=True)

    return router
