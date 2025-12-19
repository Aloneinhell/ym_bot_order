import asyncio
import os
from datetime import datetime, timedelta

import aiohttp
import dotenv

from config import moscow_tz

dotenv.load_dotenv()
API_KEY = os.getenv('YM_KEY')
C_ID = os.getenv('CAMPAIGN_ID')


class YMService:

    BASE_URL = 'https://api.partner.market.yandex.ru/v2/'

    def __init__(self, api_key):
        self.headers = {"Api-Key": api_key}

    async def get_all_orders_shop(self, c_id):
        url = f"{self.BASE_URL}campaigns/{c_id}/orders"
        params = {'fake': 'True'}
        async with aiohttp.ClientSession() as session:
            try:
                #real
                async with session.get(url=url, headers=self.headers) as response:
                #async with session.get(url=url, headers=self.headers, params=params) as response:
                    response_text = await response.text()
                    print(f"\n\n📄 Тело ответа: {response_text}")
                    response.raise_for_status()  # Проверка на ошибки HTTP

                    data = await response.json()
                    orders_data = data['orders']

                    return orders_data
            except aiohttp.ClientError as e:
                # Это исключение теперь сработает, но тело мы уже прочитали выше
                print(f"❌ Исключение aiohttp: {e}")
                return None

    async def get_today_orders(self, c_id):
        today_msk = datetime.now(moscow_tz)
        # Форматируем в dd-mm-YYYY
        today_formatted = today_msk.strftime('%d-%m-%Y')
        print(today_formatted)  # Например: 10-12-2025
        order_data = await self.get_all_orders_shop(c_id=c_id)
        today_orders = []
        for order in order_data:
            order_datetime = order['creationDate']
            order_date = order_datetime[0:10]

            if order_date == today_formatted:
                order_details = await self.get_order_detail(c_id=c_id, order_id=order['id'])
                today_orders.append(order_details)
        return today_orders

    async def get_order_detail(self, c_id, order_id):
        url = f"{self.BASE_URL}campaigns/{c_id}/orders/{order_id}"
        params = {'fake': 'True'}
        async with aiohttp.ClientSession() as session:
            try:
                #real
                async with session.get(url=url, headers=self.headers) as response:
                #async with session.get(url=url, headers=self.headers, params=params) as response:
                    response.raise_for_status()  # Проверка на ошибки HTTP
                    data = await response.json()
                    order = data['order']
                    items = order['items']
                    order_datetime = order['creationDate']
                    items_list = []
                    for item in items:
                        items_list.append({'article': item['offerId'], 'name': item['offerName'],
                                           'id': item['id'],
                                           'count': item['count']})
                    order_details = {'order_id': order['id'], 'items': items_list,
                                     'status': order['status'], 'date': order_datetime}

                    #print(f"\n\nDETAILS:\n{order_details}\n\n")

                    return order_details
            except aiohttp.ClientError as e:
                print(f"Ошибка запроса: {e}")
                return None

    async def get_shops(self):
        url = f"{self.BASE_URL}campaigns/"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url=url, headers=self.headers) as response:
                    response.raise_for_status()  # Проверка на ошибки HTTP
                    data = await response.json()
                    campaigns = data['campaigns']
                    print(f"\n\n{campaigns}\n\n")
                    return campaigns
            except aiohttp.ClientError as e:
                print(f"Ошибка запроса: {e}")
                return None

    async def send_product(self, order_id, c_id, items):
        url = f"{self.BASE_URL}campaigns/{c_id}/orders/{order_id}/deliverDigitalGoods"
        body = {'items': items}

        try:
            async with aiohttp.ClientSession() as session:
                print(f"\n📤 Отправка запроса на: {url}")
                print(f"📦 Тело запроса: {body}")

                async with session.post(
                        url,
                        json=body,
                        headers=self.headers,
                        timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    # Читаем тело ответа ВНЕ зависимости от статуса
                    response_text = await response.text()
                    print(f"📥 Статус ответа: {response.status}")
                    print(f"📄 Тело ответа: {response_text}")

                    # Теперь бросаем исключение, если статус не 2xx
                    response.raise_for_status()

                    # Если дошли сюда, статус успешный
                    data = await response.json()
                    print(f"✅ Успех: {data}")
                    return data

        except aiohttp.ClientError as e:
            # Это исключение теперь сработает, но тело мы уже прочитали выше
            print(f"❌ Исключение aiohttp: {e}")
            return None
# y_s = YMService(api_key=API_KEY)
# asyncio.run(y_s.get_shops())
