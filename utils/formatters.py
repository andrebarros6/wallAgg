from typing import Union

def format_currency(value: Union[float, int], currency: str) -> str:
    """Format currency display"""
    if currency.upper() == 'BTC':
        return f"₿{value:.8f}"
    elif currency.upper() == 'ETH':
        return f"Ξ{value:.6f}"
    elif currency.upper() == 'EUR':
        return f"€{value:,.2f}"
    else:  # USD default
        return f"${value:,.2f}"

def format_balance(balance: float, symbol: str) -> str:
    """Format token balance"""
    if balance >= 1000:
        return f"{balance:,.2f} {symbol}"
    elif balance >= 1:
        return f"{balance:.4f} {symbol}"
    else:
        return f"{balance:.8f} {symbol}"

def shorten_address(address: str, start: int = 6, end: int = 4) -> str:
    """Shorten blockchain address for display"""
    if len(address) <= start + end:
        return address
    return f"{address[:start]}...{address[-end:]}"
