import re
from typing import Tuple

class InputValidator:
    """Validate user inputs for security"""

    # Ethereum address pattern
    ETH_ADDRESS_PATTERN = re.compile(r'^0x[a-fA-F0-9]{40}$')

    # Bitcoin address patterns (simplified)
    BTC_ADDRESS_PATTERN = re.compile(r'^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}$')

    @staticmethod
    def validate_eth_address(address: str) -> Tuple[bool, str]:
        """Validate Ethereum address"""
        if not address:
            return False, "Address cannot be empty"

        if not InputValidator.ETH_ADDRESS_PATTERN.match(address):
            return False, "Invalid Ethereum address format (must be 0x + 40 hex chars)"

        return True, "Valid"

    @staticmethod
    def validate_btc_address(address: str) -> Tuple[bool, str]:
        """Validate Bitcoin address"""
        if not address:
            return False, "Address cannot be empty"

        if not InputValidator.BTC_ADDRESS_PATTERN.match(address):
            return False, "Invalid Bitcoin address format"

        return True, "Valid"

    @staticmethod
    def validate_api_key(api_key: str, min_length: int = 16) -> Tuple[bool, str]:
        """Validate API key format"""
        if not api_key:
            return False, "API key cannot be empty"

        if len(api_key) < min_length:
            return False, f"API key too short (minimum {min_length} characters)"

        # Check for suspicious patterns
        if api_key.lower() == 'test' or api_key == '1234567890':
            return False, "API key appears to be a test/placeholder value"

        return True, "Valid"

    @staticmethod
    def sanitize_account_name(name: str) -> str:
        """Sanitize account name for display"""
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\'&]', '', name)
        return sanitized.strip()[:100]  # Limit length
