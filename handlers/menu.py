import os

import dotenv
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from config import bot
from keyboards import inline
from services.utils.get_api_creds import get_cur_cabinet, get_cur_shop
from services.utils.orders_service import OrdersService
from services.ym.ym_service import YMService


dotenv.load_dotenv()
#C_ID = os.getenv('CAMPAIGN_ID')


def get_menu_router():
    router = Router()

    @router.callback_query(F.data == 'orders_menu')
    async def handle_orders_menu(callback: types.CallbackQuery):
        msg_id = callback.message.message_id
        chat_id = callback.message.chat.id
        cur_cabinet = await get_cur_cabinet()
        if cur_cabinet:
            api_key = cur_cabinet.api_key
            cur_shop = await get_cur_shop()
            ym_service = YMService(api_key=api_key)
            if cur_shop:
                c_id = cur_shop.c_id
                new_orders = await ym_service.get_today_orders(c_id=c_id)
                delivered, canceled, another = await OrdersService.get_orders_count(orders=new_orders)

                text = f"ℹ️<b>Заказы за СЕГОДНЯ</b>:\n"
                await bot.edit_message_text(text=text, chat_id=chat_id, message_id=msg_id,
                                            parse_mode='HTML',
                                            reply_markup=inline.orders_menu_kb(another_orders=another,
                                                                               delivered_orders=delivered,
                                                                               canceled_orders=canceled))
        else:
            text = f"<b>😔Не нашли магазинов в этом кабинете...</b>"
            await bot.edit_message_text(text=text, chat_id=chat_id, message_id=msg_id,
                                        parse_mode='HTML',
                                        reply_markup=inline.back_kb())

    @router.callback_query(F.data == 'back_button')
    async def handle_back_button(callback: types.CallbackQuery, state: FSMContext):
        chat_id = callback.message.chat.id
        state_data = await state.get_data()
        is_cabinet_setted = False
        is_shop_setted = False
        try:
            is_cabinet_setted = state_data['is_cabinet_setted']
            is_shop_setted = state_data['is_shop_setted']
        except:
            ...
        finally:
            text = f"<b>✅Мы в меню!</b>\n\n" \
                   f"Чем вам помочь?"
            if is_cabinet_setted and is_shop_setted:
                cur_cabinet = await get_cur_cabinet()
                cur_shop = await get_cur_shop()
                text += f"<blockquote>Кабинет: {cur_cabinet.b_id}\n" \
                        f"Магазин: {cur_shop.c_id} / {cur_shop.domain}" \
                        f"</blockquote>"
            await bot.edit_message_text(text=text, chat_id=chat_id, message_id=callback.message.message_id,
                                        parse_mode='HTML',
                                        reply_markup=inline.menu_kb(is_cabinet_setted=is_cabinet_setted,
                                                                    is_shop_setted=is_shop_setted))

    @router.callback_query(F.data == 'del_msg')
    async def handle_del_msg(callback: types.CallbackQuery):
        chat_id = callback.message.chat.id
        msg_id = callback.message.message_id
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        await callback.answer()

    return router
