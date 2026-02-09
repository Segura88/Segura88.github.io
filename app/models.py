from sqlalchemy import Column, Integer, DateTime, Text, String, UniqueConstraint
from .database import Base

class WeeklyMemory(Base):
    __tablename__ = "weekly_memories"

    id = Column(Integer, primary_key=True)
    week_monday = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)    
    text = Column(Text, nullable=False)
    author = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("week_monday", "author", name="one_memory_per_author_per_week"),
    )


class EmailToken(Base):
    __tablename__ = "email_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String, nullable=False, unique=True)
    author = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Integer, nullable=False, default=0)


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    author = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)


class UnlinkedMemory(Base):
    __tablename__ = "unlinked_memories"

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    author = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
