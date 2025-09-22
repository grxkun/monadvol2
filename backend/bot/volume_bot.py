"""Core volume bot implementation."""
import asyncio
import logging
import random
import time
from typing import Optional, Dict, Any
from datetime import datetime

from web3 import Web3
from web3.exceptions import TransactionNotFound, ContractLogicError
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.config import BotConfig

logger = logging.getLogger(__name__)


class VolumeBot:
    """Volume trading bot that executes trades at random intervals."""
    
    def __init__(self, config: BotConfig):
        self.config = config
        self.w3 = Web3(Web3.HTTPProvider(config.rpc_url))
        self.account = self.w3.eth.account.from_key(config.private_key)
        self.is_running = False
        self.trade_count = 0
        self.last_trade_time: Optional[datetime] = None
        self.next_trade_time: Optional[datetime] = None
        
        # Basic ERC20 ABI for token transfers
        self.erc20_abi = [
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]
        
        try:
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(config.contract_address),
                abi=self.erc20_abi
            )
        except Exception as e:
            logger.error(f"Failed to initialize contract: {e}")
            self.contract = None
    
    def _get_next_trade_delay(self) -> int:
        """Get random delay for next trade."""
        return random.randint(
            self.config.min_interval_seconds,
            self.config.max_interval_seconds
        )
    
    async def _execute_trade(self) -> Dict[str, Any]:
        """Execute a single trade transaction."""
        if not self.contract:
            raise Exception("Contract not initialized")
        
        try:
            # Get current balance
            balance = self.contract.functions.balanceOf(self.account.address).call()
            decimals = self.contract.functions.decimals().call()
            
            # Convert trade amount to wei
            trade_amount_wei = int(self.config.trade_amount * (10 ** decimals))
            
            if balance < trade_amount_wei:
                raise Exception(f"Insufficient balance. Required: {trade_amount_wei}, Available: {balance}")
            
            # Create a self-transfer to generate volume
            transaction = self.contract.functions.transfer(
                self.account.address,
                trade_amount_wei
            ).build_transaction({
                'from': self.account.address,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.config.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            self.trade_count += 1
            self.last_trade_time = datetime.now()
            
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'block_number': receipt.blockNumber,
                'gas_used': receipt.gasUsed,
                'trade_amount': self.config.trade_amount,
                'timestamp': self.last_trade_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def start(self):
        """Start the volume bot."""
        if not self.config.validate():
            raise Exception("Invalid configuration")
        
        self.is_running = True
        logger.info("Volume bot started")
        
        while self.is_running and self.config.is_active:
            try:
                # Execute trade
                result = await self._execute_trade()
                
                if result['success']:
                    logger.info(f"Trade #{self.trade_count} executed successfully: {result['tx_hash']}")
                else:
                    logger.error(f"Trade failed: {result['error']}")
                
                # Calculate next trade time
                delay = self._get_next_trade_delay()
                self.next_trade_time = datetime.fromtimestamp(time.time() + delay)
                logger.info(f"Next trade scheduled in {delay} seconds at {self.next_trade_time}")
                
                # Wait for next trade
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"Bot error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def stop(self):
        """Stop the volume bot."""
        self.is_running = False
        logger.info("Volume bot stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status."""
        return {
            'is_running': self.is_running,
            'is_active': self.config.is_active,
            'trade_count': self.trade_count,
            'last_trade_time': self.last_trade_time.isoformat() if self.last_trade_time else None,
            'next_trade_time': self.next_trade_time.isoformat() if self.next_trade_time else None,
            'config': {
                'contract_address': self.config.contract_address,
                'trade_amount': self.config.trade_amount,
                'min_interval_seconds': self.config.min_interval_seconds,
                'max_interval_seconds': self.config.max_interval_seconds
            }
        }