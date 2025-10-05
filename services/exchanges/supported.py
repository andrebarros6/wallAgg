from typing import Dict, List

class SupportedExchanges:
    """Registry of supported exchanges and their capabilities"""

    EXCHANGES = {
        'binance': {
            'name': 'Binance',
            'oauth': False,
            'api_key_required': True,
            'features': ['spot', 'futures', 'margin'],
            'docs_url': 'https://www.binance.com/en/support/faq/360002502072'
        },
        'coinbase': {
            'name': 'Coinbase',
            'oauth': True,
            'api_key_required': True,
            'features': ['spot'],
            'docs_url': 'https://help.coinbase.com/en/exchange/managing-my-account/how-to-create-an-api-key'
        },
        'kraken': {
            'name': 'Kraken',
            'oauth': False,
            'api_key_required': True,
            'features': ['spot', 'futures', 'margin'],
            'docs_url': 'https://support.kraken.com/hc/en-us/articles/360000919966'
        },
        'kucoin': {
            'name': 'KuCoin',
            'oauth': False,
            'api_key_required': True,
            'features': ['spot', 'futures'],
            'docs_url': 'https://www.kucoin.com/support/360015102174'
        },
        'bybit': {
            'name': 'Bybit',
            'oauth': False,
            'api_key_required': True,
            'features': ['spot', 'derivatives'],
            'docs_url': 'https://www.bybit.com/en-US/help-center/bybitHC_Article?id=000001823'
        },
        'okx': {
            'name': 'OKX',
            'oauth': False,
            'api_key_required': True,
            'features': ['spot', 'futures', 'options'],
            'docs_url': 'https://www.okx.com/support/hc/en-us/articles/360006475091'
        }
    }

    @staticmethod
    def get_exchange_list() -> List[str]:
        """Get list of supported exchange IDs"""
        return list(SupportedExchanges.EXCHANGES.keys())

    @staticmethod
    def get_exchange_info(exchange_id: str) -> Dict:
        """Get information about a specific exchange"""
        return SupportedExchanges.EXCHANGES.get(exchange_id, {})

    @staticmethod
    def supports_oauth(exchange_id: str) -> bool:
        """Check if exchange supports OAuth"""
        info = SupportedExchanges.get_exchange_info(exchange_id)
        return info.get('oauth', False)

    @staticmethod
    def get_api_permissions_required() -> List[str]:
        """Get required API permissions (for all exchanges)"""
        return [
            'Read account balances',
            'View spot account'
        ]

    @staticmethod
    def get_api_permissions_forbidden() -> List[str]:
        """Get forbidden API permissions"""
        return [
            'Enable withdrawals',
            'Enable trading',
            'Enable transfers',
            'Enable futures trading',
            'Enable margin trading'
        ]
