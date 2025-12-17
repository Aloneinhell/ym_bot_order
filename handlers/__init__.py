from aiogram import Router

from handlers.cabinets import get_cabinets_router
from handlers.excel_load import get_excel_eater_router
from handlers.menu import get_menu_router
from handlers.orders import get_orders_router
from handlers.shops import get_shops_router
from handlers.start import get_start_router


def get_full_router() -> Router:
    """Создает и возвращает роутер для пользовательских команд."""
    router = Router()
    router.include_router(get_start_router())
    router.include_router(get_menu_router())
    router.include_router(get_orders_router())
    router.include_router(get_cabinets_router())
    router.include_router(get_shops_router())
    router.include_router(get_excel_eater_router())

    return router
