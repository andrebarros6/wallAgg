import requests
from typing import Dict, List
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings
from services.blockchain.base import BlockchainClient
from services.security.validation import InputValidator

class EthereumClient(BlockchainClient):
    """Etherscan API client for Ethereum data"""

    BASE_URL = "https://api.etherscan.io/api"

    def __init__(self):
        self.api_key = settings.ETHERSCAN_API_KEY
        if not self.api_key:
            raise ValueError("ETHERSCAN_API_KEY not set in environment variables. Please add it to your .env file.")

    def validate_address(self, address: str) -> bool:
        """Validate Ethereum address"""
        valid, _ = InputValidator.validate_eth_address(address)
        return valid

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_native_balance(self, address: str) -> Dict:
        """Get ETH balance"""
        if not self.validate_address(address):
            raise ValueError(f"Invalid Ethereum address: {address}")

        params = {
            'module': 'account',
            'action': 'balance',
            'address': address,
            'tag': 'latest',
            'apikey': self.api_key
        }

        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data['status'] != '1':
            raise ValueError(f"Etherscan API error: {data.get('message', 'Unknown error')}")

        # Convert Wei to ETH
        balance_wei = int(data['result'])
        balance_eth = balance_wei / 1e18

        return {
            'symbol': 'ETH',
            'balance': balance_eth,
            'address': address
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_token_balances(self, address: str) -> List[Dict]:
        """Get ERC-20 token balances"""
        if not self.validate_address(address):
            raise ValueError(f"Invalid Ethereum address: {address}")

        # Get list of ERC-20 transactions to find tokens
        params = {
            'module': 'account',
            'action': 'tokentx',
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'sort': 'desc',
            'apikey': self.api_key
        }

        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data['status'] != '1' or not data['result']:
            return []

        # Extract unique token contracts
        token_contracts = {}
        for tx in data['result']:
            contract = tx['contractAddress']
            if contract not in token_contracts:
                token_contracts[contract] = {
                    'symbol': tx['tokenSymbol'],
                    'decimals': int(tx['tokenDecimal']) if tx['tokenDecimal'] else 18,
                    'name': tx['tokenName']
                }

        # Get balance for each token (limit to 10 tokens to avoid rate limits)
        tokens = []
        for contract, info in list(token_contracts.items())[:10]:
            try:
                balance = self._get_token_balance(address, contract)
                if balance > 0:
                    tokens.append({
                        'symbol': info['symbol'],
                        'balance': balance / (10 ** info['decimals']),
                        'token_address': contract,
                        'name': info['name']
                    })
            except Exception as e:
                # Skip tokens that fail to fetch
                continue

        return tokens

    def _get_token_balance(self, address: str, contract: str) -> int:
        """Get balance for specific ERC-20 token"""
        params = {
            'module': 'account',
            'action': 'tokenbalance',
            'contractaddress': contract,
            'address': address,
            'tag': 'latest',
            'apikey': self.api_key
        }

        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data['status'] == '1':
            return int(data['result'])
        return 0

    def get_wallet_data(self, address: str) -> Dict:
        """Get complete wallet data (native + tokens)"""
        native = self.get_native_balance(address)
        tokens = self.get_token_balances(address)

        return {
            'native': native,
            'tokens': tokens
        }
