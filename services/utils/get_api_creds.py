from sqlalchemy import select

from data.database import AsyncSessionLocal
from data.models import Cabinets, Shops


async def get_cur_cabinet():
    async with AsyncSessionLocal() as session:
        cur_shop = await get_cur_shop()
        b_id = cur_shop.b_id
        cur_cabinet = await session.scalar(select(Cabinets).where(Cabinets.b_id == b_id))
        return cur_cabinet


async def get_cur_shop():
    async with AsyncSessionLocal() as session:
        cur_shop = await session.scalar(select(Shops).where(Shops.is_chosen == True))

        return cur_shop


async def get_api_keys():
    async with AsyncSessionLocal() as session:
        api_keys = []
        cabinets_res = await session.scalars(select(Cabinets))
        if cabinets_res:
            cabinets = cabinets_res.all()
            if cabinets:
                for cabinet in cabinets:
                    api_keys.append(cabinet.api_key)

                return api_keys

