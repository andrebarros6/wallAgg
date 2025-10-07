import requests
from typing import Dict, List
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from config.settings import settings
from services.blockchain.base import BlockchainClient
from services.security.validation import InputValidator
import logging

logger = logging.getLogger(__name__)

class EthereumClient(BlockchainClient):
    """Etherscan API client for Ethereum data"""

    BASE_URL = "https://api.etherscan.io/v2/api"
    CHAIN_ID = 1  # Ethereum mainnet

    # Top ERC-20 tokens by market cap (prioritize checking these first)
    MAJOR_TOKENS = {
        '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48': {'symbol': 'USDC', 'decimals': 6, 'name': 'USD Coin'},
        '0xdAC17F958D2ee523a2206206994597C13D831ec7': {'symbol': 'USDT', 'decimals': 6, 'name': 'Tether USD'},
        '0x6B175474E89094C44Da98b954EedeAC495271d0F': {'symbol': 'DAI', 'decimals': 18, 'name': 'Dai Stablecoin'},
        '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': {'symbol': 'WETH', 'decimals': 18, 'name': 'Wrapped Ether'},
        '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': {'symbol': 'WBTC', 'decimals': 8, 'name': 'Wrapped Bitcoin'},
        '0x514910771AF9Ca656af840dff83E8264EcF986CA': {'symbol': 'LINK', 'decimals': 18, 'name': 'ChainLink Token'},
        '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984': {'symbol': 'UNI', 'decimals': 18, 'name': 'Uniswap'},
        '0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0': {'symbol': 'MATIC', 'decimals': 18, 'name': 'Matic Token'},
        '0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e': {'symbol': 'YFI', 'decimals': 18, 'name': 'yearn.finance'},
        '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9': {'symbol': 'AAVE', 'decimals': 18, 'name': 'Aave Token'},
        '0x4d224452801ACEd8B2F0aebE155379bb5D594381': {'symbol': 'APE', 'decimals': 18, 'name': 'ApeCoin'},
        '0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE': {'symbol': 'SHIB', 'decimals': 18, 'name': 'SHIBA INU'},
        '0x6982508145454Ce325dDbE47a25d4ec3d2311933': {'symbol': 'PEPE', 'decimals': 18, 'name': 'Pepe'},
        '0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84': {'symbol': 'stETH', 'decimals': 18, 'name': 'Lido Staked Ether'},
    }

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
            'chainid': self.CHAIN_ID,
            'module': 'account',
            'action': 'balance',
            'address': address,
            'tag': 'latest',
            'apikey': self.api_key
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            logger.info(f"Etherscan API response: {data}")

            if data['status'] != '1':
                error_msg = data.get('message', 'Unknown error')
                result = data.get('result', '')

                # Handle specific error cases
                if 'invalid api key' in error_msg.lower() or 'invalid api key' in result.lower():
                    raise ValueError("Invalid Etherscan API key. Please check your ETHERSCAN_API_KEY in .env file")
                elif 'rate limit' in error_msg.lower() or 'rate limit' in result.lower():
                    raise ValueError("Etherscan API rate limit exceeded. Please wait a moment and try again")
                elif 'deprecated' in error_msg.lower() or 'deprecated' in result.lower():
                    raise ValueError("Etherscan API error: Using deprecated V1 endpoint. Please update to V2 (already fixed in code, restart app)")
                else:
                    raise ValueError(f"Etherscan API error: {error_msg}")

            # Convert Wei to ETH
            balance_wei = int(data['result'])
            balance_eth = balance_wei / 1e18

            return {
                'symbol': 'ETH',
                'balance': balance_eth,
                'address': address
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error calling Etherscan API: {e}")
            raise ValueError(f"Network error: Unable to connect to Etherscan API. Please check your internet connection")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_token_balances(self, address: str) -> List[Dict]:
        """Get ERC-20 token balances with smart prioritization"""
        if not self.validate_address(address):
            raise ValueError(f"Invalid Ethereum address: {address}")

        tokens = []
        checked_contracts = set()

        # STEP 1: Check major tokens first (most likely to have value)
        logger.info(f"Checking {len(self.MAJOR_TOKENS)} major tokens...")
        for contract, info in self.MAJOR_TOKENS.items():
            try:
                balance = self._get_token_balance(address, contract)
                if balance > 0:
                    tokens.append({
                        'symbol': info['symbol'],
                        'balance': balance / (10 ** info['decimals']),
                        'token_address': contract,
                        'name': info['name']
                    })
                    logger.info(f"Found {info['symbol']}: {balance / (10 ** info['decimals'])}")
                checked_contracts.add(contract.lower())
            except Exception as e:
                logger.debug(f"Error checking {info['symbol']}: {e}")
                continue

        # STEP 2: Get token transaction history
        params = {
            'chainid': self.CHAIN_ID,
            'module': 'account',
            'action': 'tokentx',
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'sort': 'desc',
            'apikey': self.api_key
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data['status'] != '1' or not data['result']:
                return tokens  # Return major tokens if no transaction history
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching token transactions: {e}")
            return tokens  # Return major tokens found so far

        # STEP 3: Extract unique tokens from transaction history
        token_contracts = {}
        for tx in data['result']:
            contract = tx['contractAddress'].lower()
            if contract not in checked_contracts and contract not in token_contracts:
                token_contracts[contract] = {
                    'symbol': tx['tokenSymbol'],
                    'decimals': int(tx['tokenDecimal']) if tx['tokenDecimal'] else 18,
                    'name': tx['tokenName']
                }

        # STEP 4: Check additional tokens from history (limit to 20 more)
        logger.info(f"Checking up to 20 additional tokens from transaction history...")
        additional_count = 0
        max_additional = 20

        for contract, info in token_contracts.items():
            if additional_count >= max_additional:
                break

            try:
                balance = self._get_token_balance(address, contract)
                if balance > 0:
                    tokens.append({
                        'symbol': info['symbol'],
                        'balance': balance / (10 ** info['decimals']),
                        'token_address': contract,
                        'name': info['name']
                    })
                    logger.info(f"Found {info['symbol']}: {balance / (10 ** info['decimals'])}")
                additional_count += 1
            except Exception as e:
                logger.debug(f"Error checking {info['symbol']}: {e}")
                additional_count += 1
                continue

        logger.info(f"Total tokens found: {len(tokens)}")
        return tokens

    def _get_token_balance(self, address: str, contract: str) -> int:
        """Get balance for specific ERC-20 token"""
        params = {
            'chainid': self.CHAIN_ID,
            'module': 'account',
            'action': 'tokenbalance',
            'contractaddress': contract,
            'address': address,
            'tag': 'latest',
            'apikey': self.api_key
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data['status'] == '1':
                return int(data['result'])
            else:
                # Log error but return 0 (might be invalid contract)
                logger.debug(f"Token balance check failed for {contract}: {data.get('message', 'Unknown')}")
                return 0
        except (requests.exceptions.RequestException, ValueError) as e:
            # Network error or invalid response - return 0
            logger.debug(f"Error fetching token balance for {contract}: {e}")
            return 0

    def get_wallet_data(self, address: str) -> Dict:
        """Get complete wallet data (native + tokens)"""
        native = self.get_native_balance(address)
        tokens = self.get_token_balances(address)

        return {
            'native': native,
            'tokens': tokens
        }
