import ccxt
from typing import Dict, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

class ExchangeClient:
    """Unified exchange client using CCXT"""

    SUPPORTED_EXCHANGES = {
        'binance': ccxt.binance,
        'coinbase': ccxt.coinbase,
        'kraken': ccxt.kraken,
        'kucoin': ccxt.kucoin,
        'bybit': ccxt.bybit,
        'okx': ccxt.okx
    }

    def __init__(self, exchange_name: str):
        """Initialize exchange client"""
        if exchange_name not in self.SUPPORTED_EXCHANGES:
            raise ValueError(f"Unsupported exchange: {exchange_name}. Supported: {list(self.SUPPORTED_EXCHANGES.keys())}")

        self.exchange_name = exchange_name
        self.exchange_class = self.SUPPORTED_EXCHANGES[exchange_name]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def test_connection(self, api_key: str, api_secret: str) -> bool:
        """Test exchange connection with credentials"""
        exchange = self.exchange_class({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })

        try:
            # Try to fetch balance (read-only operation)
            exchange.fetch_balance()
            return True
        except Exception as e:
            raise ValueError(f"Connection test failed: {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch_balances(self, api_key: str, api_secret: str) -> List[Dict]:
        """Fetch all balances from exchange"""
        exchange = self.exchange_class({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })

        balance_data = exchange.fetch_balance()

        # Extract non-zero balances
        balances = []
        for symbol, amounts in balance_data['total'].items():
            if amounts and amounts > 0:
                balances.append({
                    'symbol': symbol,
                    'balance': amounts
                })

        return balances

    def get_exchange_info(self) -> Dict:
        """Get exchange information"""
        exchange = self.exchange_class()
        return {
            'name': exchange.name,
            'id': exchange.id,
            'countries': exchange.countries if hasattr(exchange, 'countries') else [],
            'has_spot': exchange.has.get('spot', False) if hasattr(exchange, 'has') else True,
            'rate_limit': exchange.rateLimit if hasattr(exchange, 'rateLimit') else 1000
        }
