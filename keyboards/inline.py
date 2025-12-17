from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def menu_kb(is_cabinet_setted, is_shop_setted):
    if is_cabinet_setted and is_shop_setted:
        inline_kb = [
            [
                InlineKeyboardButton(text='🚪Кабинеты', callback_data='cabinets_menu')
            ],
            [
                InlineKeyboardButton(text='⛺Магазины', callback_data='shops_menu')
            ],
            [
                InlineKeyboardButton(text='📦Заказы', callback_data='orders_menu')
            ],
            [
                InlineKeyboardButton(text='➕🔑Добавить ключи(файл)', callback_data='add_keys_file')
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb)
    if is_cabinet_setted and not is_shop_setted:
        inline_kb = [
            [
                InlineKeyboardButton(text='🚪Кабинеты', callback_data='cabinets_menu')
            ],
            [
                InlineKeyboardButton(text='⛺Магазины', callback_data='shops_menu')
            ],
            [
                InlineKeyboardButton(text='➕🔑Добавить ключи(файл)', callback_data='add_keys_file')
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb)
    if not is_cabinet_setted and not is_shop_setted:
        inline_kb = [
            [
                InlineKeyboardButton(text='🚪Кабинеты', callback_data='cabinets_menu')
            ],
            [
                InlineKeyboardButton(text='➕🔑Добавить ключи(файл)', callback_data='add_keys_file')
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb)


# def cabinets_menu_kb():
#     inline_kb = [
#         [
#             InlineKeyboardButton(text='✅Мои кабинеты', callback_data='cabinets_list')
#         ],
#         [
#             InlineKeyboardButton(text='➕🚪Добавить кабинет', callback_data='cabinets_add')
#         ]
#     ]
#     return InlineKeyboardMarkup(inline_keyboard=inline_kb)


def cabinet_switch_kb(cabinets):
    if cabinets:
        builder = InlineKeyboardBuilder()

        for cabinet in cabinets:
            button_text = f"{cabinet.b_id}"

            # Добавляем кнопку с callback_data, содержащей ID заказа
            builder.add(InlineKeyboardButton(
                text=button_text,
                callback_data=f"switch_cabinet_{cabinet.b_id}"
            ))
        builder.add(
            InlineKeyboardButton(text='➕🚪Добавить кабинет', callback_data='cabinets_add'
                                 ))
        builder.add(
            InlineKeyboardButton(text='↩️Назад в меню', callback_data='back_button'
                                 ))

        builder.adjust(1)

        return builder.as_markup()
    else:
        inline_kb = [
            [
                InlineKeyboardButton(text='➕🚪Добавить кабинет', callback_data='cabinets_add')
            ],
            [
                InlineKeyboardButton(text='↩️Назад в меню', callback_data='back_button')
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb)


def shop_switch_kb(shops: list):
    if shops:
        builder = InlineKeyboardBuilder()

        for shop in shops:
            button_text = f"{shop.domain} - {shop.c_id}"

            # Добавляем кнопку с callback_data, содержащей ID заказа
            builder.add(InlineKeyboardButton(
                text=button_text,
                callback_data=f"switch_shop_{shop.c_id}"
            ))
        builder.add(
            InlineKeyboardButton(text='↩️Назад в меню', callback_data='back_button'
                                 ))

        builder.adjust(1)

        return builder.as_markup()
    else:
        inline_kb = [
            [
              InlineKeyboardButton(text='Других магазинов нет', callback_data='no_shops_no_answer')
            ],
            [
                InlineKeyboardButton(text='↩️Назад в меню', callback_data='back_button')
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb)




def orders_menu_kb(another_orders: int, delivered_orders: int,
                   canceled_orders: int):
    inline_kb = [
        [
            InlineKeyboardButton(text=f'Доставленные ({delivered_orders})', callback_data='delivered_orders_list')
        ],
        [
            InlineKeyboardButton(text=f'Отмененные ({canceled_orders})', callback_data='canceled_orders_list')
        ],
        [
            InlineKeyboardButton(text=f'Другие ({another_orders})', callback_data='another_orders_menu')
        ],
        [
           InlineKeyboardButton(text=f"🔍Найти заказ", callback_data='find_order_menu')
        ],
        [
            InlineKeyboardButton(text='↩️Назад в меню', callback_data='back_button')
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)


def another_orders_kb(orders: list):
    builder = InlineKeyboardBuilder()

    for order in orders:
        items = order['items']
        name = ''
        for item in items:
            name += item['name']
        button_text = f"{order['order_id']} - {name}"

        # Добавляем кнопку с callback_data, содержащей ID заказа
        builder.add(InlineKeyboardButton(
            text=button_text,
            callback_data=f"order_detail_{order['order_id']}"
        ))
    builder.add(
        InlineKeyboardButton(text='↩️Назад в меню', callback_data='back_button'
                             ))

    builder.adjust(1)

    return builder.as_markup()


def order_detail_kb():
    inline_kb = [
        [
            InlineKeyboardButton(text='📧Отправить ручками', callback_data='send_manual_menu')
        ],
        [
            InlineKeyboardButton(text='↩️Назад в меню', callback_data='back_button')
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)


def del_msg():
    inline_kb = [
        [
            InlineKeyboardButton(text='❌Убрать сообщение', callback_data='del_msg')
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)


def back_kb():
    inline_kb = [
        [
            InlineKeyboardButton(text='↩️Назад в меню', callback_data='back_button')
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)

