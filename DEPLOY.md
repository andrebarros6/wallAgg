# Deployment Guide - Push to GitHub & Deploy

## Step 1: Create GitHub Repository

### Option A: Via GitHub Website (Recommended)
1. Go to https://github.com/new
2. Repository name: `wallAgg`
3. Description: "Secure cryptocurrency portfolio tracker - DeFi wallets & exchange aggregator"
4. Visibility: **Private** (recommended for security)
5. **Do NOT** initialize with README (we already have one)
6. Click "Create repository"

### Option B: Via GitHub CLI
```bash
gh repo create wallAgg --private --source=. --remote=origin
```

## Step 2: Initialize Git & Push Code

```bash
# Navigate to project
cd c:\Users\abarr\Documents\projects\walletAggregator

# Initialize git (if not already)
git init

# Create .env file (IMPORTANT: Don't commit this!)
cp .env.example .env
# Edit .env and add your ETHERSCAN_API_KEY

# Verify .gitignore exists (protects secrets)
cat .gitignore

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Crypto Portfolio Tracker MVP

Features:
- Ethereum & Bitcoin wallet tracking
- 6 exchange integrations (Binance, Coinbase, Kraken, etc.)
- Real-time pricing via CoinGecko
- Session-only credential storage (maximum security)
- SQLite database persistence
- Interactive Streamlit dashboard"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/wallAgg.git

# Push to GitHub
git push -u origin main
# OR if default branch is 'master':
git push -u origin master
```

## Step 3: Deploy to Streamlit Cloud (FREE)

### A. Prepare for Deployment

1. **Verify requirements.txt** has all dependencies
2. **Create .streamlit/config.toml** (optional, for custom settings)

```bash
mkdir .streamlit
cat > .streamlit/config.toml << 'EOF'
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"

[server]
maxUploadSize = 200
EOF
```

3. **Ensure .gitignore excludes secrets**
```bash
# Verify these are in .gitignore:
.env
*.db
data/
secrets.toml
```

### B. Deploy on Streamlit Cloud

1. **Go to**: https://share.streamlit.io/

2. **Sign in** with GitHub

3. **Click "New app"**

4. **Configure deployment**:
   - Repository: `YOUR_USERNAME/wallAgg`
   - Branch: `main` (or `master`)
   - Main file path: `wallAgg.py`

5. **Add Secrets** (IMPORTANT!):
   - Click "Advanced settings"
   - Go to "Secrets" section
   - Add your secrets in TOML format:

```toml
# Paste this in Streamlit Cloud secrets:
ETHERSCAN_API_KEY = "your_actual_etherscan_api_key_here"

# Optional (if you have them):
POLYGONSCAN_API_KEY = "your_polygonscan_key"
COINGECKO_API_KEY = "your_coingecko_key"

# Database (Streamlit Cloud provides temp storage)
DATABASE_URL = "sqlite:///data/portfolio.db"

# App settings
DEBUG = false
AUTO_REFRESH_INTERVAL = 30
PRICE_CACHE_TTL = 60
```

6. **Click "Deploy"**

7. **Wait 2-3 minutes** for deployment

8. **Your app will be live at**: `https://YOUR_APP_NAME.streamlit.app`

## Step 4: Test Deployed App

### Safe Testing Steps:

1. **Add a Test Wallet** (No API keys needed):
   - Ethereum: `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045` (Vitalik's address)
   - Bitcoin: `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa` (Genesis address)

2. **Verify Real Data**:
   - Check if balances load correctly
   - Verify prices are real-time
   - Test multi-currency switching

3. **Test Exchange (Optional - Use Demo Keys)**:
   - See "Safe Testing Options" below

## Safe Testing Options for Exchanges

### Option 1: Exchange Testnet/Sandbox APIs

**Binance Testnet**:
- URL: https://testnet.binance.vision/
- Create test account (no real money)
- Generate API keys for testing
- Modify code to use testnet endpoint:

```python
# In services/exchanges/exchange_client.py
# For testing only:
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'urls': {
        'api': 'https://testnet.binance.vision/api'  # Testnet
    }
})
```

**Coinbase Sandbox**:
- URL: https://public.sandbox.pro.coinbase.com
- Similar approach - use sandbox endpoints

### Option 2: Create Restricted Read-Only Keys

**Safe approach**:
1. Create a **new exchange account** with $0 balance
2. Generate API keys with **ONLY** these permissions:
   - ✅ Read account information
   - ✅ View balances
   - ❌ **DISABLE**: Trading, Withdrawals, Transfers
3. Deposit $0 (keep empty)
4. Use these keys for testing

### Option 3: Mock Test Mode (Recommended for Initial Testing)

Create a test flag that simulates exchange responses:

```python
# Add to .env
TEST_MODE = true

# In services/exchanges/exchange_client.py
from config.settings import settings

def fetch_balances(self, api_key: str, api_secret: str):
    if settings.TEST_MODE:
        # Return mock data for testing
        return [
            {'symbol': 'BTC', 'balance': 0.5},
            {'symbol': 'ETH', 'balance': 2.0},
            {'symbol': 'USDC', 'balance': 1000}
        ]

    # Real implementation...
```

### Option 4: Use Public Demo Accounts

Some users share demo credentials (search for "exchange API sandbox keys"):
- **Warning**: Never use these in production
- Only for understanding how the API works
- Rotate/delete immediately after testing

## Step 5: Monitoring & Maintenance

### Monitor Your Deployment

1. **Streamlit Cloud Dashboard**:
   - View logs
   - Monitor resource usage
   - Check errors

2. **Set Up Alerts** (optional):
   - Email notifications for crashes
   - Monitor API rate limits

### Update Deployed App

```bash
# Make changes locally
git add .
git commit -m "Your update message"
git push

# Streamlit Cloud auto-deploys on push!
```

## Security Checklist Before Going Public

- [ ] ✅ `.env` file is in `.gitignore`
- [ ] ✅ No API keys in code
- [ ] ✅ Secrets configured in Streamlit Cloud
- [ ] ✅ Repository is private (recommended)
- [ ] ✅ Database files excluded from git
- [ ] ✅ Session timeout configured (1 hour)
- [ ] ✅ All exchange API keys are read-only

## Troubleshooting

### "Module not found" on Streamlit Cloud
→ Add missing package to `requirements.txt`

### "Database locked" errors
→ SQLite doesn't work well on Streamlit Cloud for multiple users
→ For production, use PostgreSQL:

```toml
# In Streamlit Cloud secrets:
DATABASE_URL = "postgresql://user:pass@host:5432/dbname"
```

### API rate limits exceeded
→ Increase cache TTL in settings
→ Reduce auto-refresh frequency

## Alternative Deployment Options

### Heroku (if you need PostgreSQL)
```bash
heroku create wallAgg
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

### Render.com (Free tier)
1. Connect GitHub repo
2. Choose "Web Service"
3. Build command: `pip install -r requirements.txt`
4. Start command: `streamlit run wallAgg.py --server.port=$PORT`

### Railway.app (Modern platform)
1. Connect GitHub
2. Auto-detects Streamlit
3. One-click deploy

## Next Steps After Deployment

1. **Share URL** with trusted users for feedback
2. **Monitor logs** for any errors
3. **Collect feedback** on UX/features
4. **Add more blockchains** (Polygon, Solana, BSC)
5. **Implement OAuth** for Coinbase (no API keys needed)

---

**Your app is now live! 🎉**

Access it at: `https://YOUR_APP_NAME.streamlit.app`
