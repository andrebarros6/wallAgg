# Crypto Portfolio Tracker 💰

A secure, real-time cryptocurrency portfolio tracker that aggregates holdings across DeFi wallets and centralized exchanges.

## Features

✅ **DeFi Wallet Tracking**
- Ethereum (ETH + ERC-20 tokens)
- Bitcoin (BTC)

✅ **Exchange Integration**
- Binance, Coinbase, Kraken, KuCoin, Bybit, OKX
- Read-only API access
- Session-only credential storage (maximum security)

✅ **Real-Time Pricing**
- CoinGecko API integration
- Multi-currency support (USD, EUR, BTC, ETH)
- Price caching for performance

✅ **Portfolio Visualization**
- Interactive charts (Plotly)
- Account-based breakdown
- Total portfolio value

✅ **Security First**
- **Session-only credential storage** - API keys never saved to disk
- Automatic session expiry (1 hour)
- No private key storage (public addresses only)
- Input validation and sanitization

## Quick Start

### Prerequisites
- Python 3.10+
- Etherscan API key (free tier: https://etherscan.io/apis)

### Installation

1. **Clone repository**
```bash
git clone <your-repo-url>
cd walletAggregator
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your API keys:
# - ETHERSCAN_API_KEY=your_key_here
```

5. **Initialize database**
```bash
python -c "from database.init_db import init_database; init_database()"
```

6. **Run application**
```bash
streamlit run wallAgg.py
```

The app will open at http://localhost:8501

## Configuration

### Required API Keys

1. **Etherscan API** (for Ethereum wallets)
   - Get free key: https://etherscan.io/apis
   - Add to `.env`: `ETHERSCAN_API_KEY=your_key`

2. **CoinGecko API** (optional, for higher rate limits)
   - Free tier works without key
   - Pro tier: https://www.coingecko.com/en/api/pricing

### Exchange API Keys

**Important: Use READ-ONLY API keys**

Required permissions:
- ✅ Read account balances
- ✅ View spot account

Forbidden permissions:
- ❌ Enable withdrawals
- ❌ Enable trading
- ❌ Enable transfers

#### How to create read-only API keys:

- **Binance**: Account → API Management → Create API → Select "Enable Reading" only
- **Coinbase**: Settings → API → New API Key → Select "View" permissions only
- **Kraken**: Settings → API → Generate Key → Select "Query Funds" only

## Usage

### Adding Wallets

1. Click "Add DeFi Wallet" in sidebar
2. Enter wallet name and select blockchain
3. Paste public address (e.g., 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0)
4. Click "Add Wallet"

**Note**: Only public addresses are needed - never enter private keys!

### Adding Exchanges

1. Click "Add Exchange" in sidebar
2. Enter exchange name and select exchange
3. Enter read-only API key and secret
4. Click "Connect Exchange"

**Security**: API keys are stored in session memory only and cleared when you close the browser tab.

### Refreshing Data

- Click "🔄 Refresh All" to update all balances
- Data auto-refreshes on page load for wallets
- Exchange data requires re-entering API keys each session (for security)

## Architecture

```
walletAggregator/
├── config/              # Settings and configuration
├── database/            # SQLAlchemy models and DB operations
├── services/            # Core business logic
│   ├── blockchain/      # Ethereum, Bitcoin clients
│   ├── exchanges/       # CCXT exchange integration
│   ├── pricing/         # CoinGecko price service
│   └── security/        # Session management, validation
├── utils/               # Formatting, error handling
├── wallAgg.py          # Main Streamlit application
└── data/               # SQLite database (gitignored)
```

## Security Model

### Session-Only Credential Storage

1. **User enters API keys** → Stored in Streamlit session state (memory only)
2. **Session expires after 1 hour** → Credentials automatically cleared
3. **Browser tab closes** → All credentials erased
4. **Database stores** → Only account metadata (names, addresses, cached balances)

### What We Store
- ✅ Wallet public addresses
- ✅ Account names
- ✅ Cached holdings (for display)

### What We DON'T Store
- ❌ API keys or secrets
- ❌ Private keys or seed phrases
- ❌ Passwords or credentials

## Deployment

### Local Development
```bash
streamlit run wallAgg.py
```

### Streamlit Cloud (Recommended for MVP)
1. Push code to GitHub
2. Go to share.streamlit.io
3. Connect repository
4. Add secrets in dashboard:
   - `ETHERSCAN_API_KEY`
   - `DATABASE_URL` (optional, defaults to SQLite)
5. Deploy!

### Docker (Optional)
```bash
docker build -t portfolio-tracker .
docker run -p 8501:8501 --env-file .env portfolio-tracker
```

## Testing

Run tests with:
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=term-missing

# Specific test
pytest tests/test_security.py -v
```

## Troubleshooting

### "ETHERSCAN_API_KEY not set"
- Make sure `.env` file exists in project root
- Check that `ETHERSCAN_API_KEY=your_key` is set
- Restart the Streamlit app after adding keys

### "Invalid address format"
- Ethereum addresses must start with `0x` and be 42 characters
- Bitcoin addresses must be valid base58 or bech32 format

### "Session expired"
- Sessions expire after 1 hour for security
- Click "Start New Session" and re-enter exchange API keys

### Exchange connection fails
- Verify API keys are correct
- Ensure API keys have "Read" permissions enabled
- Check that API keys are not IP-restricted

## Roadmap

### Phase 2 (Planned)
- [ ] More blockchains (Polygon, Solana, BSC)
- [ ] OAuth integration (Coinbase)
- [ ] Historical portfolio tracking
- [ ] Transaction history
- [ ] Export to CSV/PDF

### Phase 3 (Future)
- [ ] Multi-user support with authentication
- [ ] Price alerts and notifications
- [ ] Tax reporting (capital gains)
- [ ] Mobile app
- [ ] DeFi protocol integration (Uniswap, Aave)

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - see LICENSE file for details

## Support

- **Issues**: https://github.com/your-username/walletAggregator/issues
- **Documentation**: See [spec.md](spec.md) for technical details
- **Security**: See [SECURITY.md](SECURITY.md) for security architecture

## Disclaimer

This software is for informational purposes only. Always verify balances on official exchange/blockchain platforms. The developers are not responsible for any financial decisions made based on this tool.

**Never share your private keys or seed phrases with anyone!**
