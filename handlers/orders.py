import os

import dotenv
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select

from config import bot
from data.database import AsyncSessionLocal
from data.models import SentOrders
from keyboards import inline
from services.utils.get_api_creds import get_cur_shop, get_cur_cabinet
from services.utils.orders_service import OrdersService
from services.ym.ym_service import YMService

#dotenv.load_dotenv()
#C_ID = os.getenv('CAMPAIGN_ID')

DELIVERED_ST = 'DELIVERED'
CANCELLED_ST = 'CANCELLED'


class Form(StatesGroup):
    keys_to_send = State()
    guide_to_send = State()
    order_id = State()
    order_id_to_find = State()


def get_orders_router():
    router = Router()

    @router.callback_query(F.data == 'delivered_orders_list')
    async def handle_delivered_orders_list(callback: types.CallbackQuery):
        cur_shop = await get_cur_shop()
        c_id = cur_shop.c_id

        cur_cabinet = await get_cur_cabinet()
        ym_service = YMService(api_key=cur_cabinet.api_key)
        orders = await ym_service.get_today_orders(c_id=c_id)
        chat_id = callback.message.chat.id
        msg_id = callback.message.message_id
        sorted_orders = await OrdersService.get_orders_by_status(orders=orders, status=DELIVERED_ST)
        print(f"\n\nSORTED\n{sorted_orders}\n\n")
        text = '<b>✅Доставленные заказы:</b>\n\n'
        items_list = []
        for order in sorted_orders:
            article = ''
            name = ''
            for item in order['items']:
                article = item['article']
                name = item['name']
                if len(item['name']) > 80:
                    name = item['name'][:80]
                    items_list.append({'article': article, 'name': name})
            text += f"<code>{order['order_id']}</code> - " \
                    f"{name}\n"
        await bot.edit_message_text(text=text, chat_id=chat_id,
                                    message_id=msg_id,
                                    parse_mode='HTML',
                                    reply_markup=inline.back_kb())

    @router.callback_query(F.data == 'canceled_orders_list')
    async def handle_canceled_orders_list(callback: types.CallbackQuery):
        cur_shop = await get_cur_shop()
        c_id = cur_shop.c_id
        cur_cabinet = await get_cur_cabinet()
        ym_service = YMService(api_key=cur_cabinet.api_key)

        orders = await ym_service.get_today_orders(c_id=c_id)
        chat_id = callback.message.chat.id
        msg_id = callback.message.message_id
        sorted_orders = await OrdersService.get_orders_by_status(orders=orders, status=CANCELLED_ST)
        text = '<b>❌Отмененные заказы:</b>\n\n'
        items_list = []
        for order in sorted_orders:
            article = ''
            name = ''
            for item in order['items']:
                article = item['article']
                name = item['name']
                items_list.append({'article': article, 'name': name})
            text += f"<b>🆔ID - <code>{order['order_id']}</code></b>\n" \
                    f"<blockquote>" \
                    f"🏷️Товары - {items_list}\n" \
                    f"📅Дата - {order['date']}\n" \
                    f"ℹ️Статус - {order['status']}" \
                    f"</blockquote>"
        await bot.edit_message_text(text=text, chat_id=chat_id,
                                    message_id=msg_id,
                                    parse_mode='HTML',
                                    reply_markup=inline.back_kb())

    @router.callback_query(F.data == 'another_orders_menu')
    async def handle_another_orders_menu(callback: types.CallbackQuery):
        cur_shop = await get_cur_shop()
        c_id = cur_shop.c_id

        cur_cabinet = await get_cur_cabinet()
        ym_service = YMService(api_key=cur_cabinet.api_key)
        orders = await ym_service.get_today_orders(c_id=c_id)
        chat_id = callback.message.chat.id
        msg_id = callback.message.message_id
        sorted_orders = await OrdersService.get_orders_by_status(orders=orders, status='ANOTHER')

        text = '<b>⁉️Другие заказы:</b>\n\n'
        await bot.edit_message_text(text=text, chat_id=chat_id,
                                    message_id=msg_id,
                                    parse_mode='HTML',
                                    reply_markup=inline.another_orders_kb(orders=sorted_orders))

    @router.callback_query(F.data.startswith('order_detail_'))
    async def handle_order_detail(callback: types.CallbackQuery, state: FSMContext):
        chat_id = callback.message.chat.id
        msg_id = callback.message.message_id
        order_id = callback.data[13:]
        print(order_id)
        cur_shop = await get_cur_shop()
        c_id = cur_shop.c_id

        cur_cabinet = await get_cur_cabinet()
        ym_service = YMService(api_key=cur_cabinet.api_key)
        order_details = await ym_service.get_order_detail(c_id=c_id, order_id=order_id)
        items_list = []
        article = ''
        name = ''
        print(f"\n\nORDER DET = \n{order_details}\n\n")
        items = order_details['items']
        for item in items:
            article = item['article']
            name = item['name']
            items_list.append({'article': article, 'name': name, 'count': item['count']})
        text = f"<b>🆔ID - <code>{order_details['order_id']}</code></b>\n\n" \
               f"📅Дата - {order_details['date']}\n\n" \
               f"🏷️Товары:\n"
        iii = 1
        for item in items_list:
            name = item['name']
            if len(name) > 80:
                name = item['name'][:80]
            text += f"{iii}) {name} (Кол-во: {item['count']})\n\n"
            iii += 1

        await state.update_data(order_id=order_id)
        await bot.edit_message_text(text=text, chat_id=chat_id,
                                    message_id=msg_id,
                                    parse_mode='HTML',
                                    reply_markup=inline.order_detail_kb())

    @router.callback_query(F.data == 'send_manual_menu')
    async def handle_send_manual_menu(callback: types.CallbackQuery, state: FSMContext):
        chat_id = callback.message.chat.id
        msg_id = callback.message.message_id
        state_data = await state.get_data()
        order_id = state_data['order_id']
        text = f"🔑<b>Напишите КЛЮЧИ:</b>\n" \
               f"Ключ1\n" \
               f"Ключ2\n" \
               f"И тд, каждый ключ на новой строке (ентер)\n\n" \
               f"<blockquote>Заказ - <code>{order_id}</code></blockquote>"
        sent_msg = await bot.edit_message_text(text=text, chat_id=chat_id, message_id=msg_id,
                                               parse_mode='HTML',
                                               reply_markup=inline.back_kb())
        await state.set_state(Form.keys_to_send)
        await state.update_data(msg_id=sent_msg.message_id)

    @router.message(Form.keys_to_send)
    async def handle_key_to_send(msg: types.Message, state: FSMContext):
        chat_id = msg.chat.id
        msg_id = msg.message_id
        keys = msg.text.split(sep='\n')
        state_data = await state.get_data()
        order_id = state_data['order_id']
        sent_msg_id = state_data['msg_id']
        text = f"ℹ️<b>Теперь напишите ИНСТРУКЦИЮ</b>\n" \
               f"<blockquote>Заказ - <code>{order_id}</code>\n" \
               f"ключи - {keys}</blockquote>"
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        sent_msg = await bot.edit_message_text(text=text, chat_id=chat_id, message_id=sent_msg_id,
                                               parse_mode='HTML',
                                               reply_markup=inline.back_kb())
        await state.set_state(Form.guide_to_send)
        await state.update_data(msg_id=sent_msg.message_id)
        await state.update_data(keys_to_send=keys)

    @router.message(Form.guide_to_send)
    async def handle_guide_to_send(msg: types.Message, state: FSMContext):
        chat_id = msg.chat.id
        msg_id = msg.message_id
        guide = msg.text.strip()
        state_data = await state.get_data()
        order_id = state_data['order_id']
        sent_msg_id = state_data['msg_id']
        keys = state_data['keys_to_send']
        cur_shop = await get_cur_shop()
        c_id = cur_shop.c_id

        cur_cabinet = await get_cur_cabinet()
        ym_service = YMService(api_key=cur_cabinet.api_key)
        order_details = await ym_service.get_order_detail(c_id=c_id, order_id=order_id)
        items = order_details['items']
        items_list = []
        activate_till = '2200-01-01'
        for i, item in enumerate(items):
            p_id = item['id']  # Это должен быть fulfilmentId
            key = keys[i]  # Берем соответствующий ключ

            items_list.append({
                'id': p_id,  # Используем правильное имя поля!
                'codes': [key],  # Массив с одним ключом
                'activate_till': activate_till,
                'slip': guide
            })
        send_order = await ym_service.send_product(order_id=order_id, c_id=c_id, items=items_list)
        if send_order:
            text = ''
            if send_order['status'] == 'OK':
                text = f"✅<b>Заказ <code>{order_id}</code> отработан!</b>\n" \
                       f"Отправлены ключи + инструкция\n" \
                       f"<blockquote>🔑Ключи: {keys}</blockquote>"
                async with AsyncSessionLocal() as session:
                    new_sent_order = SentOrders(
                        o_id=order_id,
                        keys=keys
                    )
                    session.add(new_sent_order)
                    await session.commit()
            else:
                text = f"😔<b>Произошла ошибка при запросе к ЯМ...</b>\n" \
                       f"Ошибка:\n" \
                       f"<blockquote><code>{send_order['status']}\n{send_order['errors']}</code></blockquote>"

            await bot.edit_message_text(text=text, chat_id=chat_id, message_id=sent_msg_id,
                                        parse_mode='HTML',
                                        reply_markup=inline.back_kb())
        else:
            text = f"😔<b>Не удалось отправить запрос к ЯМ...</b>"
            await bot.edit_message_text(text=text, chat_id=chat_id, message_id=sent_msg_id,
                                        parse_mode='HTML',
                                        reply_markup=inline.back_kb())

        await bot.delete_message(chat_id=chat_id, message_id=msg_id)

    @router.callback_query(F.data == 'find_order_menu')
    async def handle_find_order_menu(callback: types.CallbackQuery, state: FSMContext):
        chat_id = callback.message.chat.id
        msg_id = callback.message.message_id
        text = f"🆔<b>Напишите ID заказа:</b>"
        await state.set_state(Form.order_id_to_find)
        sent_msg = await bot.edit_message_text(text=text, chat_id=chat_id, message_id=msg_id,
                                               parse_mode='HTML',
                                               reply_markup=inline.back_kb())
        await state.update_data(msg_id=sent_msg.message_id)

    @router.message(Form.order_id_to_find)
    async def handle_order_id_to_find(msg: types.Message, state: FSMContext):
        chat_id = msg.chat.id
        msg_id = msg.message_id
        cur_shop = await get_cur_shop()
        c_id = cur_shop.c_id
        cur_cabinet = await get_cur_cabinet()
        api_key = cur_cabinet.api_key
        state_data = await state.get_data()
        sent_msg_id = state_data['msg_id']
        order_id = msg.text.strip()
        ym_service = YMService(api_key=api_key)
        order_details = await ym_service.get_order_detail(c_id=c_id, order_id=order_id)
        items = order_details['items']
        names = []
        item_list = []
        for item in items:
            name = item['name']
            count = item['count']
            item_list.append({'name': name, 'count': count})
        async with AsyncSessionLocal() as session:
            order = await session.scalar(select(SentOrders).where(SentOrders.o_id == order_id))
            if order and order_details:
                text = f"🆔ID - <code>{order.o_id}</code>\n" \
                       f"📅Дата - {order_details['date']}\n\n" \
                       f"Товары:\n"
                iii = 1
                for item in item_list:
                    name = item['name']
                    count = item['count']
                    name_len = len(name)
                    if name_len > 50:
                        text += f"{iii}) {name} (Кол-во: {count})\n\n"
                        iii += 1
                    else:
                        text += f"{iii}) {name}\n"
                        iii += 1
                text += f"\nКлючи:\n"
                kkk = 1
                for key in order.keys:
                    text += f"{kkk}) <code>{key}</code>\n"
                    kkk += 1
            elif not order and order_details:
                await state.update_data(order_id=order_id)
                text = f"🆔ID - <code>{order_details['order_id']}</code>\n" \
                       f"📅Дата - {order_details['date']}\n\n" \
                       f"Товары:\n"
                iii = 1
                for item in item_list:
                    name = item['name']
                    count = item['count']
                    name_len = len(name)
                    if name_len > 50:
                        text += f"{iii}) {name} (Кол-во: {count})\n\n"
                        iii += 1
                    else:
                        text += f"{iii}) {name}\n"
                        iii += 1
            else:
                text = f"😓<b>Заказ не найден</b>"
        kb = inline.back_kb()
        wait_statuses = ['PROCESSING', 'PENDING']
        if order_details['status'] in wait_statuses:
            kb = inline.order_detail_kb()
        await bot.edit_message_text(text=text, chat_id=chat_id,
                                    message_id=sent_msg_id,
                                    parse_mode='HTML',
                                    reply_markup=kb)
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)

    return router
