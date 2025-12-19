from sqlalchemy import select, delete

from config import bot
from data.database import AsyncSessionLocal
from data.models import Products, Admins, Cabinets, Shops
from keyboards import inline
from services.utils.get_api_creds import get_cur_shop
from services.ym.ym_service import YMService

unsent_orders_ids = []
sent_orders_ids = []


class YmCheckerSender:

    def __init__(self, api_keys):
        self.api_keys = api_keys

    async def check_and_send(self):
        for api_key in self.api_keys:
            admins_ids = []
            async with AsyncSessionLocal() as session:
                cur_cab = await session.scalar(select(Cabinets).where(Cabinets.api_key == api_key))
                ym_service = YMService(api_key=cur_cab.api_key)
                shops_res = await session.scalars(select(Shops).where(Shops.b_id == cur_cab.b_id))

                if shops_res:
                    shops = shops_res.all()
                    for shop in shops:
                        c_id = shop.c_id
                        print(f"\n\nApi:\n{api_key}\n\nB-id:\n{cur_cab.b_id}\n\nC-id:\n{c_id}\n")
                        today_orders = await ym_service.get_today_orders(c_id=c_id)
                        admins_res = await session.scalars(select(Admins))
                        if admins_res:
                            admins = admins_res.all()
                            if admins:
                                for admin in admins:
                                    admins_ids.append(admin.tg_id)

                            activate_till = '2200-01-01'
                            if today_orders:
                                for order in today_orders:
                                    if order['status'] in ('PROCESSING', 'PENDING'):
                                        items = order['items']
                                        items_list = []
                                        all_keys_found = True
                                        # Список для хранения ID отправленных ключей
                                        used_product_ids = []

                                        for item in items:
                                            article = item['article']
                                            count = item['count']  # количество товара в заказе

                                            # Ищем ВСЕ ключи для этого артикула
                                            products_res = await session.scalars(
                                                select(Products).where(Products.p_art == article)
                                            )
                                            products = products_res.all()
                                            print(f"\n\nTODAY - {today_orders}\n\n"
                                                  f"ORder = {order}\n\n"
                                                  f"Prods = {products}")
                                            # Проверяем, достаточно ли ключей
                                            if len(products) < count:
                                                all_keys_found = False
                                                break  # выходим из цикла - не хватает ключей
                                            else:
                                                # Берём нужное количество ключей (и их ID)
                                                selected_products = products[:count]
                                                keys = [product.p_key for product in selected_products]
                                                # Сохраняем ID отправленных ключей для удаления
                                                used_product_ids.extend([product.id for product in selected_products])
                                                # Инструкция берётся из первого продукта (у всех одинаковые)
                                                guide = products[0].p_guide if products else ''

                                                items_list.append({
                                                    'id': item['id'],
                                                    'codes': keys,  # массив из count ключей
                                                    'activate_till': activate_till,
                                                    'slip': guide
                                                })

                                        # Теперь обрабатываем весь заказ целиком
                                        if not all_keys_found:
                                            if order['order_id'] not in unsent_orders_ids:
                                                text = f"По заказу <code>{order['order_id']}</code> <b>Нет ключей</b>\n\n" \
                                                       f"<b>Отправьте ручками!</b>"
                                                for tg_id in admins_ids:
                                                    await bot.send_message(chat_id=tg_id, text=text,
                                                                           parse_mode='HTML',
                                                                           reply_markup=inline.del_msg())
                                                unsent_orders_ids.append(order['order_id'])
                                            continue  # переходим к следующему заказу

                                        # Если все ключи найдены
                                        if order['order_id'] not in sent_orders_ids:
                                            try:
                                                send_product = await ym_service.send_product(
                                                    c_id=c_id,
                                                    items=items_list,
                                                    order_id=order['order_id']
                                                )

                                                if send_product:
                                                    # Формируем текст уведомления
                                                    text = f"📤 По заказу <code>{order['order_id']}</code>\nОтправлены товары:\n"

                                                    for idx, item in enumerate(items, 1):
                                                        text += f"\n{idx}) {item['name']} x{item['count']}\n"

                                                    text += f"\n🔑 Ключи:\n"
                                                    for sent_item in items_list:
                                                        keys = sent_item['codes']
                                                        keys_str = ', '.join(keys)
                                                        text += f"<code>{keys_str}</code>\n"

                                                    sent_orders_ids.append(order['order_id'])

                                                    for tg_id in admins_ids:
                                                        await bot.send_message(
                                                            chat_id=tg_id,
                                                            text=text,
                                                            parse_mode='HTML',
                                                            reply_markup=inline.del_msg()
                                                        )

                                                    # ✅ УДАЛЯЕМ ОТПРАВЛЕННЫЕ КЛЮЧИ ИЗ БД
                                                    if used_product_ids:
                                                        try:
                                                            delete_stmt = delete(Products).where(Products.id.in_(used_product_ids))
                                                            await session.execute(delete_stmt)
                                                            await session.commit()
                                                            print(
                                                                f"✅ Удалено {len(used_product_ids)} ключей из БД для заказа {order['order_id']}")
                                                        except Exception as delete_error:
                                                            print(f"⚠️ Ошибка при удалении ключей: {delete_error}")
                                                            await session.rollback()

                                                else:
                                                    # Если send_product вернул False
                                                    raise Exception("API вернул ошибку")

                                            except Exception as e:
                                                # Ошибка при отправке
                                                if order['order_id'] not in unsent_orders_ids:
                                                    text = f"По заказу <code>{order['order_id']}</code>\n" \
                                                           f"<b>Ошибка при отправке:</b> {str(e)[:100]}\n\n" \
                                                           f"<b>Отправьте ручками!</b>"
                                                    for tg_id in admins_ids:
                                                        await bot.send_message(
                                                            chat_id=tg_id,
                                                            text=text,
                                                            parse_mode='HTML',
                                                            reply_markup=inline.del_msg()
                                                        )
                                                    unsent_orders_ids.append(order['order_id'])