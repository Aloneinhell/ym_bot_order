from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select

from config import bot
from data.database import AsyncSessionLocal
from data.models import Cabinets, Shops
from keyboards import inline
from services.utils.get_api_creds import get_cur_shop
from services.ym.ym_service import YMService


class Form(StatesGroup):
    api_key = State()
    is_cabinet_setted = State()


def get_cabinets_router():
    router = Router()

    @router.callback_query(F.data == 'cabinets_menu')
    async def handle_cabinets_menu(callback: types.CallbackQuery, state: FSMContext):
        chat_id = callback.message.chat.id
        msg_id = callback.message.message_id
        state_data = await state.get_data()
        async with AsyncSessionLocal() as session:
            cabinets_res = await session.scalars(select(Cabinets))
            if cabinets_res:
                cabinets = cabinets_res.all()
                cabinets_list = []
                if cabinets:
                    chosen_cabinet = ''
                    for cabinet in cabinets:
                        if cabinet.is_chosen:
                            chosen_cabinet = cabinet.b_id
                        else:
                            cabinets_list.append(cabinet)
                    await state.update_data(is_cabinet_setted=True)
                    text = f"<b>Текущий кабинет:\n" \
                           f"Business_id: {chosen_cabinet}</b>\n" \
                           f"<blockquote>Чтобы выбрать другой кабинет нажмите на кнопку</blockquote>"
                    await bot.edit_message_text(text=text, chat_id=chat_id, message_id=msg_id,
                                                parse_mode='HTML',
                                                reply_markup=inline.cabinet_switch_kb(cabinets=cabinets_list))
                else:
                    text = f"<b>😞Нет ни одного кабинета...\n\n</b>" \
                           f"Добавьте!"
                    await bot.edit_message_text(text=text, chat_id=chat_id, message_id=msg_id,
                                                parse_mode='HTML',
                                                reply_markup=inline.cabinet_switch_kb(cabinets=cabinets_list))

    @router.callback_query(F.data == 'cabinets_add')
    async def handle_cabinets_add(callback: types.CallbackQuery, state: FSMContext):
        chat_id = callback.message.chat.id
        msg_id = callback.message.message_id
        text = f"<b>🗝️Напишите API-ключ от кабинета:</b>"
        sent_msg = await bot.edit_message_text(text=text, chat_id=chat_id, message_id=msg_id,
                                               parse_mode='HTML',
                                               reply_markup=inline.back_kb())
        await state.update_data(msg_id=sent_msg.message_id)
        await state.set_state(Form.api_key)

    @router.message(Form.api_key)
    async def handle_api_key(msg: types.Message, state: FSMContext):
        chat_id = msg.chat.id
        msg_id = msg.message_id
        state_data = await state.get_data()
        sent_msg_id = state_data['msg_id']
        async with AsyncSessionLocal() as session:
            api_key = msg.text.strip()
            ym_service = YMService(api_key=api_key)
            shops = await ym_service.get_shops()
            is_chosen = False
            business = {}
            if shops:
                for shop in shops:
                    if not is_chosen:
                        is_chosen = True
                    business = shop['business']

                    new_shop = Shops(
                        c_id=shop['id'],
                        domain=shop['domain'],
                        b_id=business['id'],
                        is_chosen=is_chosen
                    )

                    session.add(new_shop)
                    await session.commit()
                b_id = business['id']
                new_cabinet = Cabinets(
                    api_key=api_key,
                    b_id=b_id,
                    is_chosen=True
                )
                session.add(new_cabinet)
                await session.commit()

                added_shops_res = await session.scalars(select(Shops))
                added_shops = added_shops_res.all()
                cur_shop = await get_cur_shop()
                shops_list = []
                text = f'<b>✅Добавлены магазины:</b>\n\n'
                for shop in added_shops:
                    shops_list.append({'c_id': shop.c_id,
                                       'domain': shop.domain})
                for shop in shops_list:
                    text += f"<blockquote>{shop['c_id']} - {shop['domain']}</blockquote>\n"
                text += f"\n\nТекущий магазин - <b>{cur_shop.c_id} - {cur_shop.domain}</b>"

                await bot.edit_message_text(text=text, chat_id=chat_id, message_id=sent_msg_id,
                                            parse_mode='HTML',
                                            reply_markup=inline.back_kb())
                await bot.delete_message(chat_id=chat_id, message_id=msg_id)
                await state.update_data(is_cabinet_setted=True)
                await state.update_data(is_shop_setted=True)
    return router
