# Volume Trading Bot v2

A Python executable volume bot that trades specific amounts to specific contract addresses between specific time intervals, complete with a web dashboard for configuration and monitoring. Fully Vercel production-ready.

## Features

🤖 **Automated Volume Trading**
- Configurable trade amounts and time intervals
- Random interval execution between min/max ranges
- ERC-20 token support
- Ethereum blockchain integration

📊 **Web Dashboard**
- Real-time bot status monitoring
- Configuration management interface
- Trade execution logs and statistics
- Responsive design with Tailwind CSS

🚀 **Production Ready**
- Vercel deployment configuration
- FastAPI backend with async support
- Next.js frontend with server-side rendering
- SQLite database for persistence

## Architecture

```
monadvol2/
├── backend/                 # Python FastAPI backend
│   ├── app.py              # Main FastAPI application
│   ├── bot/                # Bot core logic
│   │   ├── volume_bot.py   # Trading bot implementation
│   │   ├── config.py       # Configuration management
│   │   └── scheduler.py    # Time interval management
│   ├── api/                # API endpoints
│   │   └── routes.py       # REST API routes
│   └── database.py         # SQLite database operations
├── frontend/               # Next.js React frontend
│   ├── pages/              # Next.js pages
│   ├── components/         # React components
│   │   ├── Dashboard.js    # Main dashboard
│   │   ├── ConfigForm.js   # Configuration form
│   │   └── ExecutionLog.js # Trade logs display
│   └── styles/             # CSS styles
└── vercel.json             # Vercel deployment config
```

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/grxkun/monadvol2.git
cd monadvol2

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd frontend && npm install && cd ..
```

### 2. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Blockchain Configuration
RPC_URL=https://rpc.ankr.com/eth
PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE
CONTRACT_ADDRESS=0xTOKEN_CONTRACT_ADDRESS

# Trading Configuration
TRADE_AMOUNT=0.01
MIN_INTERVAL_SECONDS=300    # 5 minutes
MAX_INTERVAL_SECONDS=1800   # 30 minutes

# Bot Control
BOT_ACTIVE=false
```

### 3. Local Development

**Start Backend:**
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Start Frontend:**
```bash
cd frontend
npm run dev
```

Visit `http://localhost:3000` to access the dashboard.

## Deployment to Vercel

### 1. Setup Vercel Project

```bash
npm install -g vercel
vercel login
vercel
```

### 2. Configure Environment Variables

In your Vercel dashboard, add these environment variables:

- `RPC_URL`: Your Ethereum RPC endpoint
- `PRIVATE_KEY`: Your wallet private key (keep secure!)
- `CONTRACT_ADDRESS`: The ERC-20 token contract address
- `TRADE_AMOUNT`: Amount to trade per transaction
- `MIN_INTERVAL_SECONDS`: Minimum seconds between trades
- `MAX_INTERVAL_SECONDS`: Maximum seconds between trades

### 3. Deploy

```bash
vercel --prod
```

## Dashboard Features

### Configuration Panel
- **RPC URL**: Configure your Ethereum node endpoint
- **Private Key**: Set your wallet private key (encrypted in storage)
- **Contract Address**: Specify the ERC-20 token to trade
- **Trade Amount**: Set the amount per transaction
- **Time Intervals**: Configure min/max intervals between trades

### Bot Control
- **Start/Stop**: Control bot execution with one click
- **Real-time Status**: Monitor bot state and next execution time
- **Safety Features**: Validation and error handling

### Monitoring
- **Live Statistics**: Total trades, success rate, volume
- **Execution Logs**: Detailed transaction history
- **Error Tracking**: Failed transaction details

## API Endpoints

### Bot Control
- `GET /api/status` - Get bot status and statistics
- `POST /api/control` - Start/stop the bot
  ```json
  { "action": "start" | "stop" }
  ```

### Configuration
- `GET /api/config` - Get current configuration
- `POST /api/config` - Update configuration
  ```json
  {
    "rpc_url": "https://rpc.ankr.com/eth",
    "private_key": "0x...",
    "contract_address": "0x...",
    "trade_amount": 0.01,
    "min_interval_seconds": 300,
    "max_interval_seconds": 1800
  }
  ```

### Monitoring
- `GET /api/trades` - Get trade execution logs
- `GET /api/stats` - Get trading statistics
- `GET /api/health` - Health check

## Security Considerations

⚠️ **Important Security Notes:**

1. **Private Key Security**: Never share your private key. Use a dedicated wallet with limited funds.
2. **Environment Variables**: Keep sensitive data in environment variables, not in code.
3. **HTTPS Only**: Only use the bot over HTTPS in production.
4. **Limited Funds**: Use a wallet with only the necessary funds for trading.
5. **Network Security**: Ensure your RPC endpoint is secure and reliable.

## Trading Strategy

The bot implements a simple volume generation strategy:

1. **Self-Transfer**: Executes token transfers to the same wallet to generate volume
2. **Random Intervals**: Uses random delays between min/max intervals to appear natural
3. **Gas Optimization**: Estimates and uses appropriate gas prices
4. **Error Handling**: Gracefully handles network issues and transaction failures

## Monitoring and Logging

- **Real-time Dashboard**: Web interface for monitoring
- **SQLite Database**: Persistent storage of configuration and logs
- **Transaction Tracking**: Full history of all trades with links to Etherscan
- **Error Logging**: Detailed error messages and stack traces
- **Statistics**: Success rates, volume totals, and performance metrics

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Database Schema
- `config`: Bot configuration settings
- `trade_logs`: Transaction execution history

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation
- Review the logs in the dashboard

---

**Disclaimer**: This software is for educational purposes. Trading cryptocurrencies involves risk. Use at your own discretion and never trade with funds you cannot afford to lose.