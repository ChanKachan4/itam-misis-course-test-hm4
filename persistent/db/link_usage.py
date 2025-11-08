from sqlalchemy import Column, Text, DateTime
from .link import utcnow, _uuid4_at_str
from sqlalchemy.orm import declarative_base
from .base import Base


class LinkUsage(Base):
    __tablename__ = "link_usage"

    id = Column(Text, default=_uuid4_at_str, primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    link_id = Column(Text, nullable=False)
    user_agent = Column(Text, nullable=False)
    ip = Column(Text, nullable=False)
