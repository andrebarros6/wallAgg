import requests
from typing import Dict, List
from tenacity import retry, stop_after_attempt, wait_exponential
from services.blockchain.base import BlockchainClient
from services.security.validation import InputValidator

class BitcoinClient(BlockchainClient):
    """Blockchain.com API client for Bitcoin data"""

    BASE_URL = "https://blockchain.info"

    def validate_address(self, address: str) -> bool:
        """Validate Bitcoin address"""
        valid, _ = InputValidator.validate_btc_address(address)
        return valid

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_native_balance(self, address: str) -> Dict:
        """Get BTC balance"""
        if not self.validate_address(address):
            raise ValueError(f"Invalid Bitcoin address: {address}")

        response = requests.get(f"{self.BASE_URL}/balance?active={address}")
        response.raise_for_status()
        data = response.json()

        if address not in data:
            raise ValueError(f"Address not found: {address}")

        # Convert satoshis to BTC
        balance_satoshis = data[address]['final_balance']
        balance_btc = balance_satoshis / 1e8

        return {
            'symbol': 'BTC',
            'balance': balance_btc,
            'address': address
        }

    def get_token_balances(self, address: str) -> List[Dict]:
        """Bitcoin doesn't have tokens"""
        return []

    def get_wallet_data(self, address: str) -> Dict:
        """Get Bitcoin wallet data"""
        native = self.get_native_balance(address)

        return {
            'native': native,
            'tokens': []
        }
