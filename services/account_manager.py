from typing import Dict, List, Optional
from services.security.session_manager import SecureSessionManager
from services.blockchain.ethereum import EthereumClient
from services.blockchain.bitcoin import BitcoinClient
from services.exchanges.exchange_client import ExchangeClient
from services.pricing.coingecko import CoinGeckoClient
from database.init_db import get_session
from database.crud import AccountCRUD, HoldingCRUD
from datetime import datetime

class AccountManager:
    """Manage accounts and fetch data using session credentials"""

    def __init__(self):
        self.price_client = CoinGeckoClient()
        self.blockchain_clients = {}

        # Initialize blockchain clients only if API keys are available
        try:
            self.blockchain_clients['ethereum'] = EthereumClient()
        except ValueError as e:
            print(f"Warning: Ethereum client not available - {e}")

        # Bitcoin doesn't require API key
        self.blockchain_clients['bitcoin'] = BitcoinClient()

    def add_wallet_account(self, name: str, blockchain: str, address: str) -> Dict:
        """Add wallet account and fetch data"""
        if blockchain not in self.blockchain_clients:
            raise ValueError(f"Unsupported blockchain: {blockchain}")

        client = self.blockchain_clients[blockchain]

        # Validate address
        if not client.validate_address(address):
            raise ValueError(f"Invalid {blockchain} address")

        # Fetch wallet data
        wallet_data = client.get_wallet_data(address)

        # Create account object
        account = {
            'id': f"wallet_{blockchain}_{address[:8]}",
            'type': 'wallet',
            'name': name,
            'blockchain': blockchain,
            'address': address,
            'data': wallet_data,
            'last_updated': datetime.now()
        }

        return account

    def add_exchange_account(self, name: str, exchange: str, api_key: str, api_secret: str) -> Dict:
        """Add exchange account with session-stored credentials"""
        exchange_client = ExchangeClient(exchange)

        # Test connection
        try:
            exchange_client.test_connection(api_key, api_secret)
        except Exception as e:
            raise ValueError(f"Failed to connect to {exchange}: {str(e)}")

        # Fetch initial data
        balances = exchange_client.fetch_balances(api_key, api_secret)

        # Generate account ID
        account_id = f"exchange_{exchange}_{name.lower().replace(' ', '_')}"

        # Store credentials in session
        SecureSessionManager.store_credential(account_id, api_key, api_secret)

        # Create account object (NO credentials stored here)
        account = {
            'id': account_id,
            'type': 'exchange',
            'name': name,
            'exchange': exchange,
            'data': balances,
            'last_updated': datetime.now()
        }

        return account

    def refresh_account_data(self, account: Dict) -> Dict:
        """Refresh account data"""
        if account['type'] == 'wallet':
            return self._refresh_wallet(account)
        elif account['type'] == 'exchange':
            return self._refresh_exchange(account)
        else:
            raise ValueError(f"Unknown account type: {account['type']}")

    def _refresh_wallet(self, account: Dict) -> Dict:
        """Refresh wallet data"""
        blockchain = account['blockchain']
        address = account['address']

        if blockchain not in self.blockchain_clients:
            raise ValueError(f"Blockchain client not available for {blockchain}")

        client = self.blockchain_clients[blockchain]
        wallet_data = client.get_wallet_data(address)

        account['data'] = wallet_data
        account['last_updated'] = datetime.now()
        return account

    def _refresh_exchange(self, account: Dict) -> Dict:
        """Refresh exchange data using session credentials"""
        account_id = account['id']

        # Get credentials from session
        credentials = SecureSessionManager.get_credential(account_id)
        if not credentials:
            raise ValueError(f"Session expired for {account['name']}. Please re-enter API keys.")

        # Fetch fresh data
        exchange_client = ExchangeClient(account['exchange'])
        balances = exchange_client.fetch_balances(
            credentials['api_key'],
            credentials['api_secret']
        )

        account['data'] = balances
        account['last_updated'] = datetime.now()
        return account

    def calculate_account_value(self, account: Dict, base_currency: str = 'usd') -> float:
        """Calculate total account value in base currency"""
        total = 0.0

        try:
            if account['type'] == 'wallet':
                # Native token
                if 'native' in account['data'] and account['data']['native']:
                    native = account['data']['native']
                    price = self.price_client.get_price(native['symbol'], base_currency)
                    total += native['balance'] * price

                # Tokens
                if 'tokens' in account['data']:
                    for token in account['data']['tokens']:
                        price = self.price_client.get_price(token['symbol'], base_currency)
                        total += token['balance'] * price

            elif account['type'] == 'exchange':
                for asset in account['data']:
                    price = self.price_client.get_price(asset['symbol'], base_currency)
                    total += asset['balance'] * price

        except Exception as e:
            print(f"Error calculating value for {account['name']}: {e}")
            return 0.0

        return total

    def save_account_to_db(self, account: Dict):
        """Save account metadata to database (NO credentials)"""
        session = get_session()

        try:
            if account['type'] == 'wallet':
                db_account = AccountCRUD.create_wallet(
                    session,
                    name=account['name'],
                    blockchain=account['blockchain'],
                    address=account['address']
                )
            elif account['type'] == 'exchange':
                db_account = AccountCRUD.create_exchange(
                    session,
                    name=account['name'],
                    exchange_name=account['exchange']
                )

            # Save holdings
            holdings = self._extract_holdings(account)
            if holdings:
                HoldingCRUD.update_holdings(session, db_account.id, holdings)

            account['db_id'] = db_account.id

        finally:
            session.close()

        return account

    def load_accounts_from_db(self) -> List[Dict]:
        """Load account metadata from database"""
        session = get_session()
        accounts = []

        try:
            db_accounts = AccountCRUD.get_all_accounts(session)

            for db_account in db_accounts:
                account = {
                    'id': f"{db_account.account_type}_{db_account.id}",
                    'db_id': db_account.id,
                    'type': db_account.account_type,
                    'name': db_account.name,
                    'last_updated': db_account.last_updated,
                    'data': None  # Will need refresh
                }

                if db_account.account_type == 'wallet':
                    account['blockchain'] = db_account.blockchain
                    account['address'] = db_account.wallet_address
                elif db_account.account_type == 'exchange':
                    account['exchange'] = db_account.exchange_name
                    account['requires_credentials'] = True

                # Load cached holdings
                holdings = HoldingCRUD.get_account_holdings(session, db_account.id)
                account['cached_holdings'] = [
                    {'symbol': h.symbol, 'balance': h.balance}
                    for h in holdings
                ]

                accounts.append(account)

        finally:
            session.close()

        return accounts

    def delete_all_accounts(self):
        """Delete all accounts from database"""
        session = get_session()
        try:
            # Get all accounts
            db_accounts = AccountCRUD.get_all_accounts(session)
            # Delete each one
            for db_account in db_accounts:
                AccountCRUD.delete_account(session, db_account.id)
        finally:
            session.close()

    def _extract_holdings(self, account: Dict) -> List[Dict]:
        """Extract holdings from account data for DB storage"""
        holdings = []

        if account['type'] == 'wallet':
            if 'native' in account['data'] and account['data']['native']:
                holdings.append({
                    'symbol': account['data']['native']['symbol'],
                    'balance': account['data']['native']['balance']
                })

            if 'tokens' in account['data']:
                for token in account['data']['tokens']:
                    holdings.append({
                        'symbol': token['symbol'],
                        'balance': token['balance'],
                        'token_address': token.get('token_address')
                    })

        elif account['type'] == 'exchange':
            for asset in account['data']:
                holdings.append({
                    'symbol': asset['symbol'],
                    'balance': asset['balance']
                })

        return holdings
