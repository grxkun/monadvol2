"""Configuration management for the volume bot."""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class BotConfig:
    """Bot configuration class."""
    
    # Blockchain settings
    rpc_url: str
    private_key: str
    contract_address: str
    
    # Trading settings
    trade_amount: float
    min_interval_seconds: int
    max_interval_seconds: int
    
    # Bot control
    is_active: bool = False
    
    @classmethod
    def from_env(cls) -> 'BotConfig':
        """Create config from environment variables."""
        return cls(
            rpc_url=os.getenv('RPC_URL', 'https://rpc.ankr.com/eth'),
            private_key=os.getenv('PRIVATE_KEY', ''),
            contract_address=os.getenv('CONTRACT_ADDRESS', ''),
            trade_amount=float(os.getenv('TRADE_AMOUNT', '0.01')),
            min_interval_seconds=int(os.getenv('MIN_INTERVAL_SECONDS', '300')),  # 5 minutes
            max_interval_seconds=int(os.getenv('MAX_INTERVAL_SECONDS', '1800')),  # 30 minutes
            is_active=os.getenv('BOT_ACTIVE', 'false').lower() == 'true'
        )
    
    def validate(self) -> bool:
        """Validate configuration."""
        if not self.private_key:
            raise ValueError("Private key is required")
        if not self.contract_address:
            raise ValueError("Contract address is required")
        if self.trade_amount <= 0:
            raise ValueError("Trade amount must be positive")
        if self.min_interval_seconds >= self.max_interval_seconds:
            raise ValueError("Min interval must be less than max interval")
        return True


# Global config instance
config = BotConfig.from_env()