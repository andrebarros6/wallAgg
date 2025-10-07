import requests
from typing import Dict, List
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings
from datetime import datetime

class CoinGeckoClient:
    """CoinGecko API client with caching"""

    BASE_URL = "https://api.coingecko.com/api/v3"

    # Symbol to CoinGecko ID mapping
    SYMBOL_TO_ID = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'USDC': 'usd-coin',
        'USDT': 'tether',
        'DAI': 'dai',
        'WETH': 'weth',
        'WBTC': 'wrapped-bitcoin',
        'LINK': 'chainlink',
        'UNI': 'uniswap',
        'MATIC': 'matic-network',
        'YFI': 'yearn-finance',
        'AAVE': 'aave',
        'APE': 'apecoin',
        'SHIB': 'shiba-inu',
        'PEPE': 'pepe',
        'STETH': 'staked-ether',
        'BNB': 'binancecoin',
        'SOL': 'solana',
        'ADA': 'cardano',
        'AVAX': 'avalanche-2',
        'DOT': 'polkadot',
        'XRP': 'ripple',
        'DOGE': 'dogecoin',
        'LTC': 'litecoin',
        'BCH': 'bitcoin-cash',
        'TRX': 'tron',
        'ATOM': 'cosmos',
        'XLM': 'stellar',
        'FIL': 'filecoin',
        'ETC': 'ethereum-classic'
    }

    def __init__(self):
        self.api_key = settings.COINGECKO_API_KEY
        self.cache = TTLCache(maxsize=100, ttl=settings.PRICE_CACHE_TTL)

    def _get_headers(self) -> Dict:
        """Get headers for API request"""
        headers = {'accept': 'application/json'}
        if self.api_key:
            headers['x-cg-pro-api-key'] = self.api_key
        return headers

    def get_prices(self, symbols: List[str], vs_currencies: List[str] = ['usd']) -> Dict:
        """Get prices for multiple symbols"""
        cache_key = f"{','.join(sorted(symbols))}:{','.join(sorted(vs_currencies))}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        # Convert symbols to CoinGecko IDs
        coin_ids = []
        for symbol in symbols:
            if symbol.upper() in self.SYMBOL_TO_ID:
                coin_ids.append(self.SYMBOL_TO_ID[symbol.upper()])

        if not coin_ids:
            return {}

        # Make API request with error handling
        try:
            params = {
                'ids': ','.join(coin_ids),
                'vs_currencies': ','.join(vs_currencies)
            }

            response = requests.get(
                f"{self.BASE_URL}/simple/price",
                params=params,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            # Convert back to symbol-based format
            result = {}
            for symbol in symbols:
                coin_id = self.SYMBOL_TO_ID.get(symbol.upper())
                if coin_id and coin_id in data:
                    result[symbol.upper()] = data[coin_id]

            self.cache[cache_key] = result
            return result

        except Exception as e:
            print(f"Error fetching prices from CoinGecko: {e}")
            # Return empty dict on error - let caller handle missing prices
            return {}

    def get_price(self, symbol: str, vs_currency: str = 'usd') -> float:
        """Get price for a single symbol"""
        prices = self.get_prices([symbol], [vs_currency])
        return prices.get(symbol.upper(), {}).get(vs_currency, 0)

    def get_multi_currency_price(self, symbol: str) -> Dict:
        """Get price in multiple currencies"""
        prices = self.get_prices([symbol], ['usd', 'eur', 'btc', 'eth'])
        return prices.get(symbol.upper(), {})
