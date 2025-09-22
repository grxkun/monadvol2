"""API routes for the volume bot."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import os

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.volume_bot import VolumeBot
from bot.config import BotConfig
from database import db

router = APIRouter()

# Global bot instance
bot_instance: Optional[VolumeBot] = None
bot_task: Optional[asyncio.Task] = None


class ConfigRequest(BaseModel):
    """Request model for bot configuration."""
    rpc_url: str = "https://rpc.ankr.com/eth"
    private_key: str
    contract_address: str
    trade_amount: float
    min_interval_seconds: int = 300  # 5 minutes
    max_interval_seconds: int = 1800  # 30 minutes


class BotControlRequest(BaseModel):
    """Request model for bot control."""
    action: str  # "start" or "stop"


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """Get current bot status."""
    global bot_instance
    
    if bot_instance:
        status = bot_instance.get_status()
    else:
        status = {
            'is_running': False,
            'is_active': False,
            'trade_count': 0,
            'last_trade_time': None,
            'next_trade_time': None,
            'config': {}
        }
    
    # Add database stats
    stats = db.get_stats()
    status.update(stats)
    
    return status


@router.post("/config")
async def update_config(config_request: ConfigRequest) -> Dict[str, Any]:
    """Update bot configuration."""
    try:
        # Validate private key format (basic check)
        if not config_request.private_key.startswith('0x') or len(config_request.private_key) != 66:
            raise HTTPException(status_code=400, detail="Invalid private key format")
        
        # Validate contract address format
        if not config_request.contract_address.startswith('0x') or len(config_request.contract_address) != 42:
            raise HTTPException(status_code=400, detail="Invalid contract address format")
        
        # Save to database
        config_data = {
            'contract_address': config_request.contract_address,
            'trade_amount': config_request.trade_amount,
            'min_interval_seconds': config_request.min_interval_seconds,
            'max_interval_seconds': config_request.max_interval_seconds,
            'is_active': False  # Always start inactive
        }
        
        if not db.save_config(config_data):
            raise HTTPException(status_code=500, detail="Failed to save configuration")
        
        # Update environment variables for the bot
        os.environ['RPC_URL'] = config_request.rpc_url
        os.environ['PRIVATE_KEY'] = config_request.private_key
        os.environ['CONTRACT_ADDRESS'] = config_request.contract_address
        os.environ['TRADE_AMOUNT'] = str(config_request.trade_amount)
        os.environ['MIN_INTERVAL_SECONDS'] = str(config_request.min_interval_seconds)
        os.environ['MAX_INTERVAL_SECONDS'] = str(config_request.max_interval_seconds)
        
        return {"success": True, "message": "Configuration updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")


@router.get("/config")
async def get_config() -> Dict[str, Any]:
    """Get current bot configuration."""
    config = db.get_config()
    if not config:
        return {"message": "No configuration found"}
    
    # Remove sensitive data
    safe_config = config.copy()
    return safe_config


@router.post("/control")
async def control_bot(control_request: BotControlRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Start or stop the bot."""
    global bot_instance, bot_task
    
    try:
        if control_request.action == "start":
            if bot_instance and bot_instance.is_running:
                return {"success": False, "message": "Bot is already running"}
            
            # Create new bot instance with current config
            config = BotConfig.from_env()
            config.is_active = True
            bot_instance = VolumeBot(config)
            
            # Update database
            db_config = db.get_config()
            if db_config:
                db_config['is_active'] = True
                db.save_config(db_config)
            
            # Start bot in background
            bot_task = asyncio.create_task(bot_instance.start())
            
            return {"success": True, "message": "Bot started successfully"}
            
        elif control_request.action == "stop":
            if bot_instance:
                bot_instance.stop()
                if bot_task:
                    bot_task.cancel()
                    bot_task = None
                
                # Update database
                db_config = db.get_config()
                if db_config:
                    db_config['is_active'] = False
                    db.save_config(db_config)
            
            return {"success": True, "message": "Bot stopped successfully"}
            
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'start' or 'stop'")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to control bot: {str(e)}")


@router.get("/trades")
async def get_trades(limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent trade logs."""
    return db.get_trade_logs(limit)


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """Get trading statistics."""
    return db.get_stats()


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "volume-bot-api"}