import uuid
from datetime import UTC, datetime
from .base import Base
from sqlalchemy import Column, Text, DateTime


def _uuid4_at_str() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(UTC)


class Link(Base):
    __tablename__ = "link"

    id = Column(Text, default=_uuid4_at_str, primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    short_link = Column(Text, nullable=False, unique=True)
    real_link = Column(Text, nullable=False)
