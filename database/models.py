from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    account_type = Column(String(20), nullable=False)  # 'wallet' or 'exchange'

    # Wallet-specific fields
    blockchain = Column(String(50), nullable=True)
    wallet_address = Column(String(255), nullable=True)

    # Exchange-specific fields
    exchange_name = Column(String(50), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)

    # Relationships
    holdings = relationship("Holding", back_populates="account", cascade="all, delete-orphan")

class Holding(Base):
    __tablename__ = 'holdings'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    symbol = Column(String(20), nullable=False)
    balance = Column(Float, nullable=False)
    token_address = Column(String(255), nullable=True)  # For ERC-20 tokens
    last_updated = Column(DateTime, default=datetime.now)

    # Relationships
    account = relationship("Account", back_populates="holdings")

class PriceCache(Base):
    __tablename__ = 'price_cache'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    currency = Column(String(10), nullable=False)  # USD, EUR, BTC, ETH
    price = Column(Float, nullable=False)
    cached_at = Column(DateTime, default=datetime.now)
