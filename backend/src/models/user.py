"""
User database model.
"""

from sqlalchemy import Column, Integer, String
from src.database import Base


class User(Base):
    """
    User database model.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
