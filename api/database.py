from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Float, Integer, DateTime, Text
from datetime import datetime
import os

_default_db = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/happyrobot.db")
)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{_default_db}")
# Convert plain sqlite:/// to async variant
if DATABASE_URL.startswith("sqlite:///") and not DATABASE_URL.startswith("sqlite+aiosqlite:///"):
    DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///", 1)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class CallRecord(Base):
    __tablename__ = "calls"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    mc_number = Column(String, nullable=True)
    carrier_name = Column(String, nullable=True)
    contact_name = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    load_id = Column(String, nullable=True)
    origin = Column(String, nullable=True)
    destination = Column(String, nullable=True)
    equipment_type = Column(String, nullable=True)
    loadboard_rate = Column(Float, nullable=True)
    agreed_rate = Column(Float, nullable=True)
    negotiation_rounds = Column(Integer, default=0)
    outcome = Column(String, nullable=True)  # booked, declined, no_deal, transferred, invalid_carrier
    sentiment = Column(String, nullable=True)  # positive, neutral, negative
    fmcsa_verified = Column(Integer, default=0)  # 0 = false, 1 = true
    transcript_summary = Column(Text, nullable=True)
    raw_data = Column(Text, nullable=True)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
