from sqlalchemy.orm import Session
from database.models import Account, Holding, PriceCache
from datetime import datetime
from typing import List, Optional

class AccountCRUD:
    """CRUD operations for accounts"""

    @staticmethod
    def create_wallet(session: Session, name: str, blockchain: str, address: str) -> Account:
        """Create a new wallet account"""
        account = Account(
            name=name,
            account_type='wallet',
            blockchain=blockchain,
            wallet_address=address
        )
        session.add(account)
        session.commit()
        session.refresh(account)
        return account

    @staticmethod
    def create_exchange(session: Session, name: str, exchange_name: str) -> Account:
        """Create a new exchange account (no credentials stored)"""
        account = Account(
            name=name,
            account_type='exchange',
            exchange_name=exchange_name
        )
        session.add(account)
        session.commit()
        session.refresh(account)
        return account

    @staticmethod
    def get_all_accounts(session: Session) -> List[Account]:
        """Get all active accounts"""
        return session.query(Account).filter(Account.is_active == True).all()

    @staticmethod
    def get_account_by_id(session: Session, account_id: int) -> Optional[Account]:
        """Get account by ID"""
        return session.query(Account).filter(Account.id == account_id).first()

    @staticmethod
    def delete_account(session: Session, account_id: int):
        """Soft delete account"""
        account = session.query(Account).filter(Account.id == account_id).first()
        if account:
            account.is_active = False
            session.commit()

class HoldingCRUD:
    """CRUD operations for holdings"""

    @staticmethod
    def update_holdings(session: Session, account_id: int, holdings: List[dict]):
        """Update holdings for an account"""
        # Delete existing holdings
        session.query(Holding).filter(Holding.account_id == account_id).delete()

        # Add new holdings
        for holding_data in holdings:
            holding = Holding(
                account_id=account_id,
                symbol=holding_data['symbol'],
                balance=holding_data['balance'],
                token_address=holding_data.get('token_address')
            )
            session.add(holding)

        session.commit()

    @staticmethod
    def get_account_holdings(session: Session, account_id: int) -> List[Holding]:
        """Get all holdings for an account"""
        return session.query(Holding).filter(Holding.account_id == account_id).all()
