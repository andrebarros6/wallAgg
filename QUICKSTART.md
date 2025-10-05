# Quick Start Guide 🚀

Get your Crypto Portfolio Tracker running in 5 minutes!

## Step 1: Setup Environment (2 min)

```bash
# Clone and navigate
cd walletAggregator

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Get API Keys (2 min)

### Etherscan API Key (Required for Ethereum)
1. Go to https://etherscan.io/apis
2. Sign up for free account
3. Create API key
4. Copy the key

### CoinGecko (Optional - works without key)
- Free tier: No key needed
- Pro tier: https://www.coingecko.com/en/api/pricing

## Step 3: Configure (1 min)

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your keys:
# ETHERSCAN_API_KEY=your_etherscan_api_key_here
```

Windows users:
```cmd
copy .env.example .env
notepad .env
```

## Step 4: Initialize Database (30 sec)

```bash
python -c "from database.init_db import init_database; init_database()"
```

You should see:
```
Created data/ directory
Initialized database tables
✓ Database ready
```

## Step 5: Run Application (30 sec)

```bash
streamlit run wallAgg.py
```

Browser will open at http://localhost:8501

## First Steps in the App

### Add Your First Wallet

1. **Ethereum Wallet Example**:
   - Click "Add DeFi Wallet" in sidebar
   - Name: "My ETH Wallet"
   - Blockchain: ethereum
   - Address: Your public Ethereum address (0x...)
   - Click "Add Wallet"

2. **Bitcoin Wallet Example**:
   - Click "Add DeFi Wallet"
   - Name: "My BTC Wallet"
   - Blockchain: bitcoin
   - Address: Your public Bitcoin address
   - Click "Add Wallet"

### Add Exchange (Optional)

**⚠️ Important: Create READ-ONLY API keys first!**

1. **On Exchange Platform**:
   - Go to API settings
   - Create new API key
   - Enable ONLY "Read" or "View" permissions
   - Copy API Key and Secret

2. **In App**:
   - Click "Add Exchange" in sidebar
   - Enter name and select exchange
   - Paste API Key and Secret
   - Click "Connect Exchange"

## Verify It's Working

✅ You should see:
- Your wallet balances displayed
- Real-time prices in USD
- Portfolio total value
- Interactive charts

## Troubleshooting

### "ETHERSCAN_API_KEY not set"
→ Make sure you created `.env` file and added your API key

### "Invalid address format"
→ Ethereum: Must start with 0x (42 chars total)
→ Bitcoin: Check you copied the full address

### "Module not found"
→ Make sure virtual environment is activated
→ Run `pip install -r requirements.txt` again

### App won't start
→ Check Python version: `python --version` (need 3.10+)
→ Try: `python -m streamlit run wallAgg.py`

## Next Steps

- 📖 Read [README.md](README.md) for full documentation
- 🔒 Read [SECURITY.md](SECURITY.md) for security details
- 🛠️ Read [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for development guide

## Need Help?

- Check existing [GitHub Issues](https://github.com/your-repo/issues)
- Create new issue with:
  - Error message
  - Steps to reproduce
  - Your Python version
  - Operating system

## Security Reminder

✅ **Safe to share**:
- Public wallet addresses
- Account names

❌ **NEVER share**:
- Private keys
- Seed phrases
- API keys with withdrawal permissions

Your session credentials are stored in memory only and cleared when you close the browser!
