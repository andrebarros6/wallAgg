from abc import ABC, abstractmethod
from typing import Dict, List

class BlockchainClient(ABC):
    """Abstract base class for blockchain clients"""

    @abstractmethod
    def get_native_balance(self, address: str) -> Dict:
        """Get native token balance (ETH, BTC, etc.)"""
        pass

    @abstractmethod
    def get_token_balances(self, address: str) -> List[Dict]:
        """Get token balances (ERC-20, etc.)"""
        pass

    @abstractmethod
    def validate_address(self, address: str) -> bool:
        """Validate address format"""
        pass
