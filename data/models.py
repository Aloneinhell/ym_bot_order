from sqlalchemy import Integer, String, DateTime, BigInteger, Float, Boolean
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class Products(Base):
    __tablename__ = 'ym_products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    p_name: Mapped[str] = mapped_column(String, nullable=False)
    p_key: Mapped[str] = mapped_column(String, nullable=False)
    p_guide: Mapped[str] = mapped_column(String, nullable=False)
    p_art: Mapped[str] = mapped_column(String, nullable=False)


class Cabinets(Base):
    __tablename__ = 'ym_cabinets'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    api_key: Mapped[str] = mapped_column(String, nullable=False)
    b_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_chosen: Mapped[bool] = mapped_column(Boolean, nullable=False)


class Shops(Base):
    __tablename__ = 'ym_shops'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    c_id: Mapped[int] = mapped_column(Integer, nullable=False)
    b_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    domain: Mapped[str] = mapped_column(String, nullable=False)
    is_chosen: Mapped[int] = mapped_column(Boolean, nullable=False)


class SentOrders(Base):
    __tablename__ = 'ym_sent_orders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    o_id: Mapped[str] = mapped_column(String, nullable=False)
    keys: Mapped[list] = mapped_column(JSONB, nullable=False)


class Admins(Base):
    __tablename__ = 'ym_admins'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
