# Crypto Portfolio Tracker - MVP Specification

## Executive Summary

Transform the current Streamlit prototype into a production-ready MVP that securely aggregates cryptocurrency holdings across DeFi wallets and centralized exchanges with real-time data integration.

---

## 1. Current State Analysis

### ✅ Implemented Features
- Streamlit-based web interface with custom styling
- Multi-account support (wallets and exchanges)
- Portfolio visualization (pie charts, bar charts)
- Multi-currency display (USD, EUR, BTC, ETH)
- Auto-refresh functionality
- Small balance filtering
- Session-based state management

### ❌ Current Limitations
- **Mock data only** - No real API integrations
- **No persistence** - Data lost on page refresh
- **Insecure** - No credential encryption or secure storage
- **Static prices** - Hardcoded conversion rates
- **No error handling** - No retry logic or failure management
- **No historical data** - Cannot track portfolio changes over time
- **No authentication** - Anyone can access the dashboard
- **Limited blockchain support** - Only basic chains listed

---

## 2. MVP Architecture

### Tech Stack

#### Core Application
- **Framework**: Streamlit (keep current)
- **Language**: Python 3.10+
- **Package Manager**: pip with requirements.txt

#### Data Layer
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy
- **Caching**: Redis (optional for MVP)

#### API Integrations
- **Blockchain Data**:
  - Etherscan API (Ethereum)
  - Blockchain.com API (Bitcoin)
  - Polygonscan API (Polygon)
  - Blockchair API (Multi-chain fallback)
- **Exchange APIs**: CCXT library (unified exchange API)
- **Price Data**: CoinGecko API (free tier)

#### Security
- **Environment Variables**: python-dotenv
- **Encryption**: cryptography library (Fernet)
- **Secrets Management**: Streamlit secrets.toml + encryption

### System Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Streamlit UI Layer                  │
├─────────────────────────────────────────────────────┤
│              Business Logic Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Account    │  │  Portfolio   │  │   Price   │ │
│  │   Manager    │  │  Calculator  │  │  Service  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
├─────────────────────────────────────────────────────┤
│              Data Access Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  Blockchain  │  │   Exchange   │  │  Database │ │
│  │   Clients    │  │   Clients    │  │    ORM    │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
├─────────────────────────────────────────────────────┤
│                 External APIs                        │
│  • Etherscan  • CCXT  • CoinGecko  • Polygonscan   │
└─────────────────────────────────────────────────────┘
```

---

## 3. Security Requirements

### Critical Security Features

#### 3.1 Credential Management
- ✅ Store API keys encrypted using Fernet symmetric encryption
- ✅ Use environment variables for master encryption key
- ✅ Never log or display full API keys
- ✅ Implement key rotation mechanism
- ❌ Never store private keys (read-only APIs only)

#### 3.2 API Key Permissions
**Exchange Requirements:**
- Read-only permissions ONLY
- No withdrawal permissions
- No trading permissions
- No transfer permissions

#### 3.3 Data Protection
- Encrypt sensitive data at rest in database
- Use HTTPS for all API communications
- Implement rate limiting to prevent abuse
- Sanitize all user inputs

#### 3.4 Access Control (Future Enhancement)
- User authentication (Streamlit Auth or external OAuth)
- Session management
- Multi-user support with data isolation

---

## 4. API Integration Plan

### 4.1 Blockchain APIs

#### Ethereum (and ERC-20 tokens)
**API**: Etherscan API
```python
# Free tier: 5 calls/second, 100,000 calls/day
GET /api?module=account&action=balance&address={address}
GET /api?module=account&action=tokentx&address={address}
GET /api?module=account&action=tokenbalance&contractaddress={token}&address={address}
```

**Implementation Priority**: HIGH (most popular DeFi ecosystem)

#### Bitcoin
**API**: Blockchain.com / Blockchair
```python
# Blockchain.com - Free, no API key required
GET /rawaddr/{address}
GET /balance?active={address}
```

**Implementation Priority**: HIGH (largest market cap)

#### Polygon
**API**: Polygonscan API (Etherscan fork)
```python
# Same interface as Etherscan
GET /api?module=account&action=balance&address={address}
```

**Implementation Priority**: MEDIUM

#### Multi-Chain Support
**API**: Blockchair (unified multi-chain API)
- Supports 18+ blockchains
- Free tier: 30 requests/minute
- Fallback for other chains

**Implementation Priority**: LOW (Phase 2)

### 4.2 Exchange APIs

#### CCXT Library Integration
**Supported Exchanges** (50+ total, focus on top exchanges):
- Binance
- Coinbase Pro / Advanced Trade
- Kraken
- KuCoin
- Bybit
- OKX

**Implementation**:
```python
import ccxt

exchange = ccxt.binance({
    'apiKey': decrypt_api_key(encrypted_key),
    'secret': decrypt_api_secret(encrypted_secret),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}  # Read-only spot balances
})

balances = exchange.fetch_balance()
```

**Rate Limiting**: Use CCXT's built-in rate limiting
**Error Handling**: Implement retry logic with exponential backoff

**Implementation Priority**: HIGH

### 4.3 Price Data

#### CoinGecko API
**Free Tier**: 10-50 calls/minute
```python
# Get multiple coin prices in one call
GET /api/v3/simple/price?ids={coin_ids}&vs_currencies=usd,eur,btc,eth
```

**Caching Strategy**:
- Cache prices for 60 seconds
- Batch requests for all coins at once
- Update on user-triggered refresh

**Fallback**: CoinMarketCap API (requires API key)

**Implementation Priority**: HIGH

---

## 5. Database Schema

### 5.1 SQLAlchemy Models

#### Accounts Table
```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    account_type VARCHAR(20) NOT NULL, -- 'wallet' or 'exchange'

    -- Wallet-specific fields
    blockchain VARCHAR(50),
    wallet_address VARCHAR(255),

    -- Exchange-specific fields
    exchange_name VARCHAR(50),
    api_key_encrypted BLOB,
    api_secret_encrypted BLOB,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,

    UNIQUE(wallet_address, blockchain),
    UNIQUE(exchange_name, api_key_encrypted)
);
```

#### Holdings Table (Current Snapshot)
```sql
CREATE TABLE holdings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    balance DECIMAL(36, 18) NOT NULL,
    token_address VARCHAR(255), -- For ERC-20 tokens
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    INDEX idx_account_symbol (account_id, symbol)
);
```

#### Price Cache Table
```sql
CREATE TABLE price_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(20) NOT NULL,
    currency VARCHAR(10) NOT NULL, -- USD, EUR, BTC, ETH
    price DECIMAL(18, 8) NOT NULL,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(symbol, currency),
    INDEX idx_cached_at (cached_at)
);
```

#### Portfolio History Table (Optional for MVP, Phase 2)
```sql
CREATE TABLE portfolio_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER,
    total_value_usd DECIMAL(18, 2),
    snapshot_data JSON, -- Full holdings snapshot
    snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    INDEX idx_snapshot_date (snapshot_date)
);
```

### 5.2 Database Utilities

```python
# database/init_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

def init_database(db_url='sqlite:///portfolio.db'):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
```

---

## 6. Feature Roadmap

### Phase 1: Core MVP (Weeks 1-3)

#### Week 1: Foundation
- [ ] Project restructuring (modular architecture)
- [ ] Database setup (SQLAlchemy models)
- [ ] Security implementation (encryption utilities)
- [ ] Environment variable configuration
- [ ] Error handling framework

#### Week 2: Data Integration
- [ ] CoinGecko price API integration
- [ ] Etherscan API client for Ethereum
- [ ] Blockchain.com API client for Bitcoin
- [ ] CCXT integration for 3 major exchanges (Binance, Coinbase, Kraken)
- [ ] Data persistence (save/load accounts from DB)

#### Week 3: Polish & Testing
- [ ] Account CRUD operations with DB
- [ ] Real-time price updates
- [ ] Portfolio calculation with live data
- [ ] Error messages and user feedback
- [ ] Basic unit tests (80% coverage target)
- [ ] Documentation updates

**MVP Success Criteria**:
✅ Users can add real wallets (ETH, BTC) and see actual balances
✅ Users can connect 3+ exchanges securely
✅ Portfolio values display in real-time
✅ Data persists between sessions
✅ No security vulnerabilities in API key storage

---

### Phase 2: Enhanced Features (Weeks 4-6)

- [ ] Additional blockchain support (Polygon, BSC, Solana)
- [ ] Transaction history viewing
- [ ] Portfolio performance tracking (historical data)
- [ ] Export functionality (CSV, PDF)
- [ ] Advanced filtering and search
- [ ] Mobile-responsive improvements
- [ ] User preferences storage
- [ ] Notification system (price alerts)

---

### Phase 3: Production Readiness (Weeks 7-8)

- [ ] User authentication system
- [ ] Multi-user support
- [ ] Cloud deployment (Streamlit Cloud / AWS / Heroku)
- [ ] PostgreSQL migration
- [ ] Logging and monitoring
- [ ] Backup and recovery procedures
- [ ] Performance optimization
- [ ] Security audit
- [ ] User documentation
- [ ] API rate limit monitoring dashboard

---

## 7. Technical Implementation

### 7.1 Project Structure

```
walletAggregator/
├── .env                      # Environment variables (gitignored)
├── .gitignore
├── requirements.txt
├── README.md
├── spec.md
├── wallAgg.py               # Main Streamlit app (refactored)
│
├── config/
│   ├── __init__.py
│   ├── settings.py          # Configuration management
│   └── secrets.py           # Secret/encryption key management
│
├── database/
│   ├── __init__.py
│   ├── models.py            # SQLAlchemy models
│   ├── init_db.py           # Database initialization
│   └── crud.py              # CRUD operations
│
├── services/
│   ├── __init__.py
│   ├── blockchain/
│   │   ├── __init__.py
│   │   ├── base.py          # Abstract blockchain client
│   │   ├── ethereum.py      # Etherscan API client
│   │   ├── bitcoin.py       # Bitcoin API client
│   │   └── polygon.py       # Polygonscan API client
│   │
│   ├── exchanges/
│   │   ├── __init__.py
│   │   ├── exchange_client.py  # CCXT wrapper
│   │   └── supported.py     # List of supported exchanges
│   │
│   ├── pricing/
│   │   ├── __init__.py
│   │   ├── coingecko.py    # CoinGecko API client
│   │   └── cache.py         # Price caching logic
│   │
│   └── security/
│       ├── __init__.py
│       ├── encryption.py    # Key encryption utilities
│       └── validation.py    # Input validation
│
├── utils/
│   ├── __init__.py
│   ├── formatters.py        # Currency formatting
│   ├── converters.py        # Price conversion
│   └── helpers.py           # General utilities
│
├── tests/
│   ├── __init__.py
│   ├── test_blockchain.py
│   ├── test_exchanges.py
│   ├── test_pricing.py
│   ├── test_security.py
│   └── test_database.py
│
└── data/
    └── portfolio.db         # SQLite database (gitignored)
```

### 7.2 Key Dependencies

```txt
# requirements.txt

# Web Framework
streamlit==1.31.0

# Data & Visualization
pandas==2.2.0
plotly==5.18.0

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9  # PostgreSQL (production)

# API Clients
ccxt==4.2.25            # Exchange APIs
requests==2.31.0        # HTTP requests
python-dotenv==1.0.0    # Environment variables

# Security
cryptography==42.0.0    # Encryption
pydantic==2.6.0         # Data validation

# Utilities
tenacity==8.2.3         # Retry logic
python-dateutil==2.8.2  # Date handling
cachetools==5.3.2       # Caching

# Testing
pytest==8.0.0
pytest-cov==4.1.0
responses==0.24.1       # Mock HTTP requests
```

### 7.3 Configuration Example

```python
# config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///data/portfolio.db"

    # API Keys (from environment)
    ETHERSCAN_API_KEY: str
    POLYGONSCAN_API_KEY: Optional[str] = None
    COINGECKO_API_KEY: Optional[str] = None  # Pro tier optional

    # Encryption
    ENCRYPTION_KEY: str  # Fernet key

    # App Settings
    DEBUG: bool = False
    AUTO_REFRESH_INTERVAL: int = 30  # seconds
    PRICE_CACHE_TTL: int = 60  # seconds

    # Rate Limiting
    ETHERSCAN_RATE_LIMIT: int = 5  # calls per second
    COINGECKO_RATE_LIMIT: int = 50  # calls per minute

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 7.4 Security Implementation

```python
# services/security/encryption.py
from cryptography.fernet import Fernet
from config.settings import settings

class EncryptionService:
    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())

    def encrypt_api_key(self, api_key: str) -> bytes:
        """Encrypt API key for storage"""
        return self.cipher.encrypt(api_key.encode())

    def decrypt_api_key(self, encrypted_key: bytes) -> str:
        """Decrypt API key for use"""
        return self.cipher.decrypt(encrypted_key).decode()

    @staticmethod
    def generate_key() -> str:
        """Generate a new Fernet key"""
        return Fernet.generate_key().decode()

# Usage in account creation
encryption_service = EncryptionService()
encrypted_key = encryption_service.encrypt_api_key(user_api_key)
```

### 7.5 Blockchain Client Example

```python
# services/blockchain/ethereum.py
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings

class EthereumClient:
    BASE_URL = "https://api.etherscan.io/api"

    def __init__(self):
        self.api_key = settings.ETHERSCAN_API_KEY

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_eth_balance(self, address: str) -> float:
        """Get ETH balance for address"""
        params = {
            'module': 'account',
            'action': 'balance',
            'address': address,
            'tag': 'latest',
            'apikey': self.api_key
        }

        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data['status'] != '1':
            raise ValueError(f"API error: {data.get('message', 'Unknown error')}")

        # Convert from Wei to ETH
        return int(data['result']) / 1e18

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_erc20_balances(self, address: str) -> list:
        """Get all ERC-20 token balances"""
        params = {
            'module': 'account',
            'action': 'tokentx',
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'sort': 'desc',
            'apikey': self.api_key
        }

        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data['status'] != '1':
            return []

        # Process and aggregate token transactions
        # ... (implementation details)
        return tokens
```

---

## 8. Testing Strategy

### 8.1 Unit Tests

**Coverage Target**: 80% minimum

**Key Test Areas**:
- ✅ Encryption/decryption functions
- ✅ Price conversion logic
- ✅ Database CRUD operations
- ✅ API response parsing
- ✅ Currency formatting
- ✅ Input validation

```python
# tests/test_security.py
import pytest
from services.security.encryption import EncryptionService

def test_encryption_round_trip():
    service = EncryptionService()
    original = "sk-test-1234567890abcdef"

    encrypted = service.encrypt_api_key(original)
    decrypted = service.decrypt_api_key(encrypted)

    assert decrypted == original
    assert encrypted != original.encode()
```

### 8.2 Integration Tests

**Mock External APIs**:
- Use `responses` library to mock HTTP requests
- Test error handling and retry logic
- Validate rate limiting

```python
# tests/test_blockchain.py
import responses
import pytest
from services.blockchain.ethereum import EthereumClient

@responses.activate
def test_get_eth_balance_success():
    responses.add(
        responses.GET,
        'https://api.etherscan.io/api',
        json={'status': '1', 'result': '1000000000000000000'},  # 1 ETH
        status=200
    )

    client = EthereumClient()
    balance = client.get_eth_balance('0x1234...')

    assert balance == 1.0
```

### 8.3 Security Testing

**Checklist**:
- [ ] API keys never logged or displayed
- [ ] No private keys stored anywhere
- [ ] SQL injection prevention (SQLAlchemy ORM)
- [ ] XSS prevention (Streamlit auto-escapes)
- [ ] HTTPS for all external requests
- [ ] Environment variables properly loaded
- [ ] Encryption key rotation capability

### 8.4 Manual Testing

**Test Cases**:
1. Add Ethereum wallet with real address → Verify correct balance
2. Add exchange with API keys → Verify balances match exchange
3. Test with invalid API keys → Verify error handling
4. Test network failures → Verify retry logic
5. Test price updates → Verify caching works
6. Restart app → Verify data persists

---

## 9. Deployment Plan

### 9.1 Local Development

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Create .env file
cat > .env << EOF
ENCRYPTION_KEY=your_generated_key
ETHERSCAN_API_KEY=your_etherscan_key
DATABASE_URL=sqlite:///data/portfolio.db
EOF

# Initialize database
python -c "from database.init_db import init_database; init_database()"

# Run app
streamlit run wallAgg.py
```

### 9.2 Production Deployment Options

#### Option A: Streamlit Cloud (Recommended for MVP)
**Pros**:
- Free tier available
- Automatic HTTPS
- Easy deployment from GitHub
- Secrets management built-in

**Cons**:
- Limited resources on free tier
- Public URL (no custom domain on free tier)

**Setup**:
1. Push code to GitHub
2. Connect Streamlit Cloud to repo
3. Add secrets in Streamlit Cloud dashboard
4. Deploy

#### Option B: Heroku
**Pros**:
- PostgreSQL add-on available
- Custom domains
- Good for multi-user apps

**Cons**:
- Paid tiers required
- More complex setup

#### Option C: AWS / DigitalOcean
**Pros**:
- Full control
- Scalable
- Professional infrastructure

**Cons**:
- Requires DevOps knowledge
- Higher cost
- More maintenance

### 9.3 Environment Variables for Production

```bash
# Production .env
ENCRYPTION_KEY=<production-key>
DATABASE_URL=postgresql://user:pass@host:5432/dbname
ETHERSCAN_API_KEY=<key>
POLYGONSCAN_API_KEY=<key>
COINGECKO_API_KEY=<key>
DEBUG=False
```

### 9.4 Database Migration

```python
# Migrate from SQLite to PostgreSQL
import pandas as pd
from sqlalchemy import create_engine

# Export from SQLite
sqlite_engine = create_engine('sqlite:///portfolio.db')
accounts_df = pd.read_sql_table('accounts', sqlite_engine)

# Import to PostgreSQL
pg_engine = create_engine('postgresql://user:pass@host/dbname')
accounts_df.to_sql('accounts', pg_engine, if_exists='append', index=False)
```

---

## 10. API Rate Limiting & Cost Analysis

### API Quotas (Free Tiers)

| Service | Free Tier Limit | Cost to Upgrade |
|---------|----------------|-----------------|
| Etherscan | 100K calls/day | $99/mo (Pro) |
| Polygonscan | 100K calls/day | $99/mo (Pro) |
| CoinGecko | 50 calls/min | $129/mo (Pro) |
| Blockchain.com | No limit | Free |
| CCXT (exchanges) | Varies by exchange | Free library |

### Optimization Strategies

1. **Caching**: Cache prices for 60s, balances for 5 minutes
2. **Batching**: Fetch multiple prices in one CoinGecko call
3. **On-Demand**: Only refresh on user action, not auto-refresh by default
4. **Rate Limiting**: Implement request queues with delays

**Estimated Monthly API Costs for 100 Active Users**:
- Free tier sufficient for MVP (<10 users)
- At scale: ~$100-200/mo for API subscriptions

---

## 11. Success Metrics

### MVP Launch Criteria

**Functional Requirements**:
- ✅ Support 2+ blockchains (ETH, BTC minimum)
- ✅ Support 3+ exchanges (Binance, Coinbase, Kraken)
- ✅ Real-time price updates (CoinGecko integration)
- ✅ Data persistence (SQLite/PostgreSQL)
- ✅ Secure API key storage (encryption)
- ✅ Portfolio visualization (charts working)

**Non-Functional Requirements**:
- ✅ Page load time <3 seconds
- ✅ API errors handled gracefully
- ✅ No security vulnerabilities
- ✅ 80% test coverage
- ✅ Mobile-responsive design

**User Experience**:
- ✅ Onboarding flow clear (<5 minutes to add first account)
- ✅ Error messages helpful and actionable
- ✅ Data accuracy verified against sources

---

## 12. Risk Assessment & Mitigation

### High-Risk Items

#### 1. API Key Security Breach
**Risk**: User API keys stolen or exposed
**Mitigation**:
- Strong encryption (Fernet)
- Never log keys
- Read-only permissions enforced
- Regular security audits

#### 2. API Rate Limiting
**Risk**: App becomes unusable due to rate limits
**Mitigation**:
- Aggressive caching
- User education on refresh limits
- Upgrade to paid tiers if needed
- Queue system for requests

#### 3. Exchange API Changes
**Risk**: CCXT library breaks with exchange updates
**Mitigation**:
- Pin CCXT version in requirements
- Test with exchanges regularly
- Monitor CCXT GitHub for breaking changes
- Implement graceful degradation

#### 4. Data Loss
**Risk**: Database corruption or accidental deletion
**Mitigation**:
- Regular automated backups
- Database transaction safety
- User export functionality
- Cloud storage for production DB

---

## 13. Future Enhancements (Post-MVP)

### Advanced Features
- 📊 Tax reporting (capital gains calculation)
- 📈 Performance analytics (ROI, profit/loss)
- 🔔 Price alerts and notifications
- 📱 Mobile app (React Native)
- 🤝 Portfolio sharing (read-only links)
- 🔄 DeFi protocol integration (Uniswap, Aave positions)
- 📊 NFT tracking
- 🌐 Multi-language support

### Technical Improvements
- GraphQL API for mobile apps
- WebSocket for real-time updates
- Machine learning price predictions
- Advanced caching (Redis cluster)
- Microservices architecture
- Kubernetes deployment

---

## 14. Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1 (MVP) | 3 weeks | Core features, real APIs, security, persistence |
| Phase 2 (Enhanced) | 3 weeks | Multi-chain, history, exports, mobile UI |
| Phase 3 (Production) | 2 weeks | Auth, deployment, monitoring, docs |
| **Total** | **8 weeks** | **Production-ready app** |

---

## 15. Getting Started

### Immediate Next Steps

1. **Week 1 Day 1**: Project restructuring
   - Create folder structure
   - Set up virtual environment
   - Install dependencies
   - Initialize git repository

2. **Week 1 Day 2**: Database setup
   - Create SQLAlchemy models
   - Write database initialization script
   - Create CRUD utilities

3. **Week 1 Day 3**: Security implementation
   - Implement encryption service
   - Set up environment variables
   - Create secrets management

4. **Week 1 Day 4-5**: First API integration
   - CoinGecko price service
   - Test with real data in UI

**By end of Week 1**: App should display real prices for hardcoded assets

---

## Appendix

### A. Useful Resources

- **Etherscan API Docs**: https://docs.etherscan.io/
- **CCXT Documentation**: https://docs.ccxt.com/
- **CoinGecko API**: https://www.coingecko.com/en/api
- **Streamlit Docs**: https://docs.streamlit.io/
- **SQLAlchemy Tutorial**: https://docs.sqlalchemy.org/

### B. Sample .env Template

```bash
# .env.example

# Encryption (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_KEY=your_fernet_key_here

# Database
DATABASE_URL=sqlite:///data/portfolio.db

# Blockchain APIs
ETHERSCAN_API_KEY=your_etherscan_api_key
POLYGONSCAN_API_KEY=your_polygonscan_api_key

# Price APIs
COINGECKO_API_KEY=  # Optional, leave empty for free tier

# App Configuration
DEBUG=True
AUTO_REFRESH_INTERVAL=30
PRICE_CACHE_TTL=60
```

### C. Contribution Guidelines

For future team members:
1. Follow PEP 8 style guide
2. Write tests for all new features (80% coverage minimum)
3. Update this spec when adding major features
4. Use type hints for function signatures
5. Document API integrations thoroughly
6. Never commit .env files or API keys

---

**Document Version**: 1.0
**Last Updated**: 2025-10-05
**Author**: Development Team
**Status**: Draft - Ready for Implementation
