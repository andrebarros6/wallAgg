# Troubleshooting Guide

## ✅ FIXED: Deployment Build Errors

### Issue 1: `pydantic-core` Build Failure (RESOLVED)

**Error Message:**
```
Failed to download and build `pydantic-core==2.16.1`
TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'
```

**Root Cause:**
- `pydantic==2.6.0` is incompatible with Python 3.13
- Streamlit Cloud was using Python 3.13.7
- `pydantic-core` Rust compilation failed

**Solution Applied:**
1. ✅ Updated `pydantic` from `2.6.0` to `>=2.10.0`
2. ✅ Updated `pydantic-settings` to `>=2.6.0`
3. ✅ Added `.python-version` file to specify Python 3.11
4. ✅ Changed all `==` to `>=` for better dependency resolution

**Status:** Fixed in commit `4d544d5`

---

## Common Deployment Issues

### Issue 2: Module Not Found Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'ccxt'
```

**Solution:**
1. Check `requirements.txt` includes the package
2. Clear Streamlit Cloud cache:
   - Go to app dashboard
   - Click "⋮" menu
   - Select "Reboot app"

### Issue 3: API Key Errors

**Symptoms:**
```
ETHERSCAN_API_KEY not set in environment variables
```

**Solution:**
1. Go to Streamlit Cloud dashboard
2. Click your app → Settings → Secrets
3. Add secrets in TOML format:
```toml
ETHERSCAN_API_KEY = "your_key_here"
```
4. Redeploy the app

### Issue 4: Database Errors

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Cause:**
- SQLite doesn't work well with multiple concurrent users on cloud platforms

**Solution:**
For production with multiple users, use PostgreSQL:

```toml
# In Streamlit secrets:
DATABASE_URL = "postgresql://user:pass@host:5432/dbname"
```

Or use Heroku Postgres add-on:
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

### Issue 5: Session State Issues

**Symptoms:**
- Data disappears on refresh
- Session expires immediately

**Solution:**
- This is expected behavior (session-only security)
- Sessions expire after 1 hour
- Exchange credentials must be re-entered each session
- Wallet data reloads from database automatically

---

## Local Development Issues

### Issue 6: Import Errors Locally

**Symptoms:**
```
ImportError: cannot import name 'Settings' from 'config.settings'
```

**Solution:**
```bash
# Ensure you're in the project directory
cd c:\Users\abarr\Documents\projects\walletAggregator

# Activate virtual environment
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Issue 7: Database Not Initialized

**Symptoms:**
```
sqlalchemy.exc.OperationalError: no such table: accounts
```

**Solution:**
```bash
# Initialize database
python -c "from database.init_db import init_database; init_database()"
```

### Issue 8: Etherscan API Rate Limits

**Symptoms:**
```
⚠️ Rate limit exceeded. Please wait a moment and try again.
```

**Solution:**
1. **Immediate fix:**
   - Wait 1-2 minutes
   - Try again

2. **Long-term fixes:**
   - Upgrade to Etherscan Pro API ($99/mo for higher limits)
   - Increase cache TTL in `.env`:
     ```
     PRICE_CACHE_TTL=120
     ```
   - Reduce refresh frequency

---

## Exchange Connection Issues

### Issue 9: Binance Connection Failed

**Error:**
```
Failed to connect to binance: Authentication failed
```

**Checklist:**
- ✅ API key and secret are correct
- ✅ API key has "Read" permissions enabled
- ✅ API key is not IP-restricted (or add Streamlit Cloud IPs)
- ✅ Account has verified identity (some exchanges require KYC)

**Test Connection:**
1. Try API keys on exchange website first
2. Check API key status/permissions
3. Regenerate keys if necessary

### Issue 10: Exchange Returns Empty Balances

**Cause:**
- Account has zero balance
- API key only has access to specific sub-accounts

**Solution:**
- This is normal if account is empty
- Check exchange for correct account type (Spot/Margin/Futures)
- Verify API key has access to the right account

---

## Testing Issues

### Issue 11: Can't Test Without API Keys

**Solution:**
Use public test wallets (no keys needed):

```python
# Ethereum (Vitalik's wallet)
address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

# Bitcoin (Genesis address)
address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
```

Or use exchange testnets:
- Binance Testnet: https://testnet.binance.vision/
- Coinbase Sandbox: https://public.sandbox.pro.coinbase.com

---

## Performance Issues

### Issue 12: App is Slow

**Optimization Tips:**

1. **Increase cache TTL:**
```python
# In .env or Streamlit secrets:
PRICE_CACHE_TTL = 120  # 2 minutes instead of 60 seconds
```

2. **Reduce API calls:**
   - Only refresh when needed
   - Don't enable auto-refresh
   - Limit number of tokens fetched

3. **Use database caching:**
   - App already caches holdings in DB
   - Wallets reload from cache on startup

---

## Security Issues

### Issue 13: API Keys Exposed in Logs

**Prevention:**
- ✅ `.env` is in `.gitignore`
- ✅ Never commit `.env` to git
- ✅ Use Streamlit secrets for deployment
- ✅ API keys stored in session memory only

**If Keys Are Compromised:**
1. **Immediately revoke** API keys on exchange
2. Generate new API keys
3. Check account for unauthorized activity
4. Update secrets in Streamlit Cloud

### Issue 14: Private Keys Requested

**Important:**
- ❌ App **NEVER** asks for private keys
- ❌ App **NEVER** asks for seed phrases
- ✅ Only public wallet addresses needed
- ✅ Only read-only exchange API keys

If any app asks for private keys: **DO NOT PROVIDE THEM!**

---

## Getting Help

### Streamlit Cloud Logs

View deployment logs:
1. Go to https://share.streamlit.io/
2. Click your app
3. Click "Manage app" → "Logs"
4. Download logs for debugging

### GitHub Issues

Report bugs:
- https://github.com/andrebarros6/wallAgg/issues
- Include:
  - Error message
  - Steps to reproduce
  - Browser/OS info
  - Streamlit Cloud logs (if deployment issue)

### Check Documentation

- [README.md](README.md) - User guide
- [SECURITY.md](SECURITY.md) - Security details
- [DEPLOY.md](DEPLOY.md) - Deployment guide
- [QUICKSTART.md](QUICKSTART.md) - Quick setup

---

## Quick Fixes Checklist

Before reporting an issue, try:

- [ ] Clear browser cache
- [ ] Reboot Streamlit Cloud app
- [ ] Verify all secrets are configured
- [ ] Check API key permissions
- [ ] Wait if hitting rate limits
- [ ] Update dependencies: `pip install -r requirements.txt --upgrade`
- [ ] Check GitHub for similar issues
- [ ] Review error logs carefully

---

**Most issues can be resolved by:**
1. ✅ Updating dependencies (fixed in latest commit)
2. ✅ Checking API key permissions
3. ✅ Configuring secrets correctly
4. ✅ Waiting for rate limits to reset
