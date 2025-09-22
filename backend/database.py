"""Simple database operations for storing bot configuration and logs."""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import contextmanager


class Database:
    """Simple SQLite database for bot operations."""
    
    def __init__(self, db_path: str = "volume_bot.db"):
        self.db_path = db_path
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def init_db(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            # Configuration table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    id INTEGER PRIMARY KEY,
                    contract_address TEXT NOT NULL,
                    trade_amount REAL NOT NULL,
                    min_interval_seconds INTEGER NOT NULL,
                    max_interval_seconds INTEGER NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Trade logs table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trade_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_hash TEXT,
                    success BOOLEAN NOT NULL,
                    trade_amount REAL,
                    gas_used INTEGER,
                    block_number INTEGER,
                    error_message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """Save bot configuration."""
        try:
            with self.get_connection() as conn:
                # Delete existing config and insert new one
                conn.execute("DELETE FROM config")
                conn.execute("""
                    INSERT INTO config (
                        contract_address, trade_amount, min_interval_seconds,
                        max_interval_seconds, is_active
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    config_data['contract_address'],
                    config_data['trade_amount'],
                    config_data['min_interval_seconds'],
                    config_data['max_interval_seconds'],
                    config_data['is_active']
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_config(self) -> Optional[Dict[str, Any]]:
        """Get current bot configuration."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM config ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error getting config: {e}")
            return None
    
    def log_trade(self, trade_result: Dict[str, Any]) -> bool:
        """Log trade execution result."""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO trade_logs (
                        tx_hash, success, trade_amount, gas_used, 
                        block_number, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    trade_result.get('tx_hash'),
                    trade_result['success'],
                    trade_result.get('trade_amount'),
                    trade_result.get('gas_used'),
                    trade_result.get('block_number'),
                    trade_result.get('error')
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error logging trade: {e}")
            return False
    
    def get_trade_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent trade logs."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM trade_logs 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting trade logs: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get trading statistics."""
        try:
            with self.get_connection() as conn:
                # Total trades
                cursor = conn.execute("SELECT COUNT(*) as total FROM trade_logs")
                total_trades = cursor.fetchone()['total']
                
                # Successful trades
                cursor = conn.execute("SELECT COUNT(*) as successful FROM trade_logs WHERE success = 1")
                successful_trades = cursor.fetchone()['successful']
                
                # Failed trades
                failed_trades = total_trades - successful_trades
                
                # Total volume
                cursor = conn.execute("SELECT SUM(trade_amount) as volume FROM trade_logs WHERE success = 1")
                result = cursor.fetchone()
                total_volume = result['volume'] if result['volume'] else 0
                
                return {
                    'total_trades': total_trades,
                    'successful_trades': successful_trades,
                    'failed_trades': failed_trades,
                    'success_rate': (successful_trades / total_trades * 100) if total_trades > 0 else 0,
                    'total_volume': total_volume
                }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                'total_trades': 0,
                'successful_trades': 0,
                'failed_trades': 0,
                'success_rate': 0,
                'total_volume': 0
            }


# Global database instance
db = Database()