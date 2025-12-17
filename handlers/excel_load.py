import time

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import bot
from data.database import AsyncSessionLocal
from data.models import Products
from keyboards import inline
from services.excel_eater import read_excel_to_dicts


class Form(StatesGroup):
    excel_file = State()


def get_excel_eater_router():
    router = Router()

    @router.callback_query(F.data == 'add_keys_file')
    async def handle_add_keys_file(callback: types.CallbackQuery, state: FSMContext):
        chat_id = callback.message.chat.id
        msg_id = callback.message.message_id
        text = f"🗒️<b>Загрузите Excel-файл:</b>"
        await state.set_state(Form.excel_file)
        sent_msg = await bot.edit_message_text(text=text, chat_id=chat_id, message_id=msg_id,
                                               parse_mode='HTML',
                                               reply_markup=inline.back_kb())
        await state.update_data(msg_id=sent_msg.message_id)

    @router.message(Form.excel_file)
    async def handle_excel_file(msg: types.Message, state: FSMContext):
        chat_id = msg.chat.id
        msg_id = msg.message_id
        state_data = await state.get_data()
        sent_msg_id = state_data['msg_id']
        if not msg.document:
            text = 'Отправьте excel-файл...'
            await bot.edit_message_text(chat_id=chat_id, message_id=sent_msg_id,
                                        text=text,
                                        reply_markup=inline.back_kb())
        if msg.document:
            file_name = msg.document.file_name

            try:
                text = "⏳ <b>Обрабатываю файл...</b>"
                # Отправляем сообщение о начале обработки
                processing_msg = await bot.edit_message_text(text=text, chat_id=chat_id, message_id=sent_msg_id,
                                                             parse_mode='HTML')
                await state.update_data(msg_id=processing_msg.message_id)
                # Скачиваем файл
                file = await bot.get_file(msg.document.file_id)
                file_bytes = await bot.download_file(file.file_path)

                # Читаем Excel и преобразуем в список словарей
                # Предполагается, что функция read_excel_to_dicts уже определена
                products_data = read_excel_to_dicts(file_bytes.read())

                if not products_data:
                    await processing_msg.edit_text("❌ Файл не содержит данных или данные не распознаны")
                    return
                async with AsyncSessionLocal() as session:
                    iii = 1

                    for product in products_data:
                        loaded_msg_id = state_data['msg_id']
                        new_product = Products(
                            p_name=product['p_name'],
                            p_key=product['p_key'],
                            p_guide=product['p_guide'],
                            p_art=product['p_art']
                        )
                        session.add(new_product)
                        await session.commit()
                        load_text = f"💾<b>Загрузка ({iii}/{len(products_data)})</b>\n" \
                                    f"\n" \
                                    f"Загружен ключ: {product['p_key']}"
                        loading_msg = await bot.edit_message_text(text=load_text, chat_id=chat_id,
                                                                  message_id=loaded_msg_id,
                                                                  parse_mode='HTML')
                        iii += 1
                        time.sleep(0.2)
                        await state.update_data(msg_id=loading_msg.message_id)
                    final_text = f"✅<b>Загрузка прошла успешно!</b>\n\n" \
                                 f"Загружено товаров - {iii}"
                    final_msg_id = state_data['msg_id']
                    await bot.edit_message_text(text=final_text, chat_id=chat_id,
                                                message_id=final_msg_id,
                                                parse_mode='HTML',
                                                reply_markup=inline.back_kb())
                    await state.clear()
                    await bot.delete_message(chat_id=chat_id, message_id=msg_id)


            except:
                ...

    return router
