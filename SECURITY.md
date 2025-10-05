# Security Architecture & Best Practices

## Table of Contents
1. [API Key Management Options](#api-key-management-options)
2. [Recommended Approach](#recommended-approach)
3. [Implementation Guide](#implementation-guide)
4. [Security Checklist](#security-checklist)
5. [Threat Model](#threat-model)
6. [Incident Response](#incident-response)

---

## 1. API Key Management Options

### Option A: Session-Only Storage (MOST SECURE - RECOMMENDED)
**How it works**: Users enter API keys each session; keys stored only in memory, never persisted

**Pros**:
- ✅ Zero risk of key theft from database breach
- ✅ No encryption key management needed
- ✅ Simplest security model
- ✅ User maintains full control of credentials
- ✅ No GDPR/compliance issues with storing credentials

**Cons**:
- ❌ Users must re-enter keys every session
- ❌ No auto-refresh between sessions
- ❌ Slightly worse UX

**Use Case**: Best for privacy-conscious users, personal use, development phase

---

### Option B: Encrypted Storage with User-Provided Password
**How it works**: Encrypt API keys using a password/passphrase user provides each session

**Pros**:
- ✅ Keys persist between sessions
- ✅ No master encryption key in codebase
- ✅ User controls encryption password
- ✅ Better UX than Option A

**Cons**:
- ❌ Password management burden on user
- ❌ If user forgets password, keys are lost
- ❌ Still need secure password storage mechanism

**Use Case**: Desktop application, single-user deployments

---

### Option C: Encrypted Storage with Master Key (CURRENT SPEC)
**How it works**: Store encrypted API keys in database, decrypt with master key in environment

**Pros**:
- ✅ Seamless UX - keys persist automatically
- ✅ Suitable for multi-user cloud deployment
- ✅ Industry standard approach

**Cons**:
- ❌ Master key becomes single point of failure
- ❌ If server compromised, all keys at risk
- ❌ Requires proper key rotation
- ❌ Compliance/regulatory considerations

**Use Case**: Production SaaS application with proper infrastructure

---

### Option D: OAuth/API Proxy (MOST SECURE FOR EXCHANGES)
**How it works**: Use exchange OAuth instead of API keys; or proxy all requests through your backend

**Pros**:
- ✅ No API keys stored anywhere
- ✅ Exchange-managed authentication
- ✅ Granular permission control
- ✅ Can revoke access easily

**Cons**:
- ❌ Not all exchanges support OAuth
- ❌ Requires backend infrastructure
- ❌ Complex implementation
- ❌ Proxy adds latency

**Exchange OAuth Support**:
- ✅ Coinbase (OAuth 2.0)
- ✅ Kraken (OAuth - beta)
- ❌ Binance (API keys only)
- ❌ KuCoin (API keys only)

**Use Case**: Production SaaS with backend infrastructure

---

### Option E: Hardware Security Module (HSM)
**How it works**: Store encryption keys in dedicated hardware (YubiKey, TPM, cloud HSM)

**Pros**:
- ✅ Military-grade security
- ✅ Keys never exposed in software
- ✅ Physical security guarantees

**Cons**:
- ❌ Expensive (cloud HSM: $1-2/hour)
- ❌ Complex setup
- ❌ Overkill for most use cases
- ❌ Requires hardware/cloud resources

**Use Case**: Enterprise/institutional deployments

---

## 2. Recommended Approach

### For MVP: **Hybrid Model (Option A + B)**

**Implementation Strategy**:

1. **Default Mode: Session-Only (No Storage)**
   - Users enter API keys each session
   - Keys stored in `st.session_state` (memory only)
   - Cleared when browser tab closes
   - Zero persistence risk

2. **Optional: Encrypted Local Storage**
   - User can opt-in to save keys locally
   - Use browser's `localStorage` with encryption
   - Encrypted with user-provided passphrase
   - Clear warning about risks

3. **For Production: OAuth + Encrypted Storage**
   - Implement OAuth for supported exchanges
   - Fallback to encrypted storage for others
   - Use cloud KMS (AWS KMS, Google Cloud KMS)

---

## 3. Implementation Guide

### Implementation A: Session-Only Storage (Recommended for MVP)

```python
# wallAgg.py - Modified account addition flow

import streamlit as st
from services.blockchain.ethereum import EthereumClient
from services.exchanges.exchange_client import ExchangeClient

# Initialize session state
if 'accounts' not in st.session_state:
    st.session_state.accounts = []
if 'api_credentials' not in st.session_state:
    st.session_state.api_credentials = {}  # In-memory only

def add_wallet_account(name: str, chain: str, address: str):
    """Add wallet without any API key storage"""
    # Wallets don't need API keys - addresses are public
    client = EthereumClient()  # Uses public API or your API key

    try:
        data = client.get_wallet_data(address)
        account = {
            'id': len(st.session_state.accounts) + 1,
            'type': 'wallet',
            'name': name,
            'chain': chain,
            'address': address,
            'data': data,
            'last_updated': datetime.now()
        }
        st.session_state.accounts.append(account)
        return True, "Wallet added successfully"
    except Exception as e:
        return False, f"Error: {str(e)}"

def add_exchange_account(name: str, exchange: str, api_key: str, api_secret: str):
    """Add exchange with session-only credential storage"""

    # Validate credentials immediately
    exchange_client = ExchangeClient(exchange)

    try:
        # Test connection
        balances = exchange_client.fetch_balances(api_key, api_secret)

        # Store credentials in memory ONLY
        credential_id = f"{exchange}_{len(st.session_state.accounts)}"
        st.session_state.api_credentials[credential_id] = {
            'api_key': api_key,
            'api_secret': api_secret
        }

        # Store account metadata (NO credentials in DB)
        account = {
            'id': len(st.session_state.accounts) + 1,
            'type': 'exchange',
            'name': name,
            'exchange': exchange,
            'credential_id': credential_id,  # Reference only
            'data': balances,
            'last_updated': datetime.now()
        }
        st.session_state.accounts.append(account)

        return True, "Exchange connected successfully"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def refresh_exchange_data(account):
    """Refresh exchange data using session credentials"""
    credential_id = account['credential_id']

    if credential_id not in st.session_state.api_credentials:
        st.error(f"⚠️ Credentials expired for {account['name']}. Please re-enter API keys.")
        return None

    creds = st.session_state.api_credentials[credential_id]
    exchange_client = ExchangeClient(account['exchange'])

    try:
        balances = exchange_client.fetch_balances(creds['api_key'], creds['api_secret'])
        account['data'] = balances
        account['last_updated'] = datetime.now()
        return balances
    except Exception as e:
        st.error(f"Failed to refresh {account['name']}: {str(e)}")
        return None

# UI Implementation
st.sidebar.markdown("### 🔐 Security Mode: Session-Only")
st.sidebar.info("API keys are never saved. You'll need to re-enter them each session.")

with st.sidebar.form("add_exchange"):
    account_name = st.text_input("Exchange Name")
    exchange = st.selectbox("Exchange", ['binance', 'coinbase', 'kraken'])

    st.markdown("#### API Credentials (Never Stored)")
    api_key = st.text_input("API Key", type="password", help="Only held in memory")
    api_secret = st.text_input("API Secret", type="password", help="Cleared on session end")

    st.warning("🔒 Keys stored in memory only. Close tab to clear.")

    if st.form_submit_button("Connect Exchange"):
        success, message = add_exchange_account(account_name, exchange, api_key, api_secret)
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)
```

**Advantages**:
- Zero storage = zero breach risk
- No encryption key management
- Simple implementation
- User maintains control

**User Experience**:
- On app open: "Welcome back! Please re-enter your exchange API keys to reload data"
- Session expires: "Session expired. Your API keys have been cleared for security."

---

### Implementation B: Optional Encrypted Browser Storage

```python
# services/security/browser_encryption.py
import streamlit as st
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os

class BrowserEncryption:
    """Client-side encryption using user passphrase"""

    @staticmethod
    def derive_key_from_passphrase(passphrase: str, salt: bytes) -> bytes:
        """Derive encryption key from user passphrase"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

    @staticmethod
    def encrypt_credentials(credentials: dict, passphrase: str) -> dict:
        """Encrypt credentials with user passphrase"""
        salt = os.urandom(16)
        key = BrowserEncryption.derive_key_from_passphrase(passphrase, salt)
        cipher = Fernet(key)

        credentials_json = json.dumps(credentials)
        encrypted = cipher.encrypt(credentials_json.encode())

        return {
            'salt': base64.b64encode(salt).decode(),
            'encrypted_data': base64.b64encode(encrypted).decode()
        }

    @staticmethod
    def decrypt_credentials(encrypted_package: dict, passphrase: str) -> dict:
        """Decrypt credentials with user passphrase"""
        salt = base64.b64decode(encrypted_package['salt'])
        encrypted_data = base64.b64decode(encrypted_package['encrypted_data'])

        key = BrowserEncryption.derive_key_from_passphrase(passphrase, salt)
        cipher = Fernet(key)

        try:
            decrypted = cipher.decrypt(encrypted_data)
            return json.loads(decrypted.decode())
        except:
            raise ValueError("Invalid passphrase or corrupted data")

# UI for optional persistence
st.sidebar.markdown("### 💾 Optional: Save Credentials Locally")

if st.sidebar.checkbox("Remember my API keys (encrypted)", value=False):
    with st.sidebar.expander("⚙️ Setup Passphrase"):
        st.warning("⚠️ **Security Notice**: Credentials will be encrypted and saved in browser storage. You are responsible for passphrase security.")

        passphrase = st.text_input("Encryption Passphrase", type="password",
                                   help="Choose a strong passphrase. This cannot be recovered if lost!")
        passphrase_confirm = st.text_input("Confirm Passphrase", type="password")

        if passphrase and passphrase == passphrase_confirm:
            if st.button("Enable Encrypted Storage"):
                # Save to browser localStorage (requires custom component)
                # For Streamlit, use session_state with export/import
                st.success("✅ Encrypted storage enabled. Your passphrase encrypts all API keys.")
        elif passphrase != passphrase_confirm:
            st.error("Passphrases don't match")
```

---

### Implementation C: OAuth for Coinbase (No API Keys)

```python
# services/exchanges/coinbase_oauth.py
import requests
from urllib.parse import urlencode
import streamlit as st

class CoinbaseOAuth:
    """Coinbase OAuth 2.0 implementation - NO API keys needed"""

    CLIENT_ID = "your_coinbase_oauth_client_id"  # Register app at Coinbase
    CLIENT_SECRET = "your_coinbase_oauth_secret"  # Store in .env
    REDIRECT_URI = "http://localhost:8501/oauth/callback"

    AUTHORIZATION_URL = "https://www.coinbase.com/oauth/authorize"
    TOKEN_URL = "https://api.coinbase.com/oauth/token"

    @staticmethod
    def get_authorization_url(state: str) -> str:
        """Generate OAuth authorization URL"""
        params = {
            'client_id': CoinbaseOAuth.CLIENT_ID,
            'redirect_uri': CoinbaseOAuth.REDIRECT_URI,
            'response_type': 'code',
            'scope': 'wallet:accounts:read,wallet:transactions:read',  # Read-only
            'state': state,  # CSRF protection
            'account': 'all'
        }
        return f"{CoinbaseOAuth.AUTHORIZATION_URL}?{urlencode(params)}"

    @staticmethod
    def exchange_code_for_token(code: str) -> dict:
        """Exchange authorization code for access token"""
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': CoinbaseOAuth.CLIENT_ID,
            'client_secret': CoinbaseOAuth.CLIENT_SECRET,
            'redirect_uri': CoinbaseOAuth.REDIRECT_URI
        }

        response = requests.post(CoinbaseOAuth.TOKEN_URL, data=data)
        response.raise_for_status()
        return response.json()  # Contains access_token, refresh_token

    @staticmethod
    def get_accounts(access_token: str) -> list:
        """Fetch accounts using OAuth access token"""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://api.coinbase.com/v2/accounts', headers=headers)
        response.raise_for_status()
        return response.json()['data']

# Streamlit UI
st.sidebar.markdown("### 🔐 Connect Coinbase (OAuth)")

if st.sidebar.button("🔗 Connect via Coinbase OAuth"):
    # Generate CSRF token
    import secrets
    state = secrets.token_urlsafe(32)
    st.session_state['oauth_state'] = state

    # Redirect to Coinbase
    auth_url = CoinbaseOAuth.get_authorization_url(state)
    st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)

# Handle OAuth callback (requires query parameters support)
query_params = st.query_params
if 'code' in query_params and 'state' in query_params:
    if query_params['state'] == st.session_state.get('oauth_state'):
        try:
            # Exchange code for token
            token_data = CoinbaseOAuth.exchange_code_for_token(query_params['code'])

            # Store access token (encrypted or session-only)
            st.session_state['coinbase_token'] = token_data['access_token']
            st.session_state['coinbase_refresh'] = token_data['refresh_token']

            # Fetch accounts
            accounts = CoinbaseOAuth.get_accounts(token_data['access_token'])
            st.success(f"✅ Connected! Found {len(accounts)} accounts")

        except Exception as e:
            st.error(f"OAuth failed: {str(e)}")
    else:
        st.error("⚠️ Security error: Invalid state parameter")
```

**Advantages**:
- No API keys to manage
- Exchange controls permissions
- Can revoke access from exchange dashboard
- Industry standard approach

---

## 4. Security Checklist

### Development Phase
- [ ] **Never commit credentials** - Add `.env`, `*.key`, `credentials.json` to `.gitignore`
- [ ] **Use environment variables** - All secrets in `.env` file
- [ ] **Read-only API permissions** - No withdrawal/transfer/trading permissions
- [ ] **Input validation** - Sanitize all user inputs (addresses, API keys)
- [ ] **HTTPS only** - All external API calls use HTTPS
- [ ] **Error messages** - Never expose sensitive data in error messages
- [ ] **Logging** - Never log API keys or secrets (redact in logs)
- [ ] **Code review** - Review all security-critical code paths

### Storage Phase (if persisting keys)
- [ ] **Encryption at rest** - All API keys encrypted with Fernet or AES-256
- [ ] **Strong key derivation** - Use PBKDF2 with 100k+ iterations
- [ ] **Secure key storage** - Master keys in KMS, HSM, or env variables (never in code)
- [ ] **Key rotation** - Ability to rotate encryption keys
- [ ] **Database security** - Encrypted connections, parameterized queries
- [ ] **Access control** - Principle of least privilege
- [ ] **Audit logging** - Log all credential access attempts

### Runtime Phase
- [ ] **Memory safety** - Clear sensitive data from memory after use
- [ ] **Session management** - Expire sessions, clear credentials on logout
- [ ] **Rate limiting** - Prevent brute force attacks
- [ ] **CSRF protection** - Validate state parameters in OAuth
- [ ] **Dependency scanning** - Regular `pip audit` or `safety check`
- [ ] **Security headers** - CSP, HSTS (if deploying web app)

### Deployment Phase
- [ ] **Environment isolation** - Separate dev/staging/prod credentials
- [ ] **Secrets management** - Use Streamlit Secrets, AWS Secrets Manager, or similar
- [ ] **Backup security** - Encrypt backups, secure backup storage
- [ ] **Monitoring** - Alert on suspicious API usage patterns
- [ ] **Incident response plan** - Document what to do if keys are compromised
- [ ] **Compliance** - GDPR, SOC 2 if handling user data

---

## 5. Threat Model

### Threat 1: Database Breach
**Scenario**: Attacker gains read access to database

**Impact**:
- ❌ Option C: All encrypted API keys exposed (decrypt if master key found)
- ✅ Option A/B: No API keys in database
- ✅ OAuth: Only access tokens exposed (revokable)

**Mitigation**:
- Use session-only storage (Option A)
- Encrypt database connections
- Regular security audits
- Implement database access logging

---

### Threat 2: Server/Application Compromise
**Scenario**: Attacker gains code execution on server

**Impact**:
- ❌ All options: Attacker can intercept API keys in memory
- ❌ Option C: Master encryption key exposed in environment

**Mitigation**:
- Deploy with minimal privileges
- Container isolation (Docker)
- Regular security patches
- Intrusion detection system
- Use OAuth (tokens can be revoked)

---

### Threat 3: Man-in-the-Middle Attack
**Scenario**: Attacker intercepts network traffic

**Impact**:
- ❌ HTTP: API keys sent in plaintext
- ✅ HTTPS: Encrypted in transit

**Mitigation**:
- **Always use HTTPS** for all API calls
- Certificate pinning (advanced)
- Validate SSL certificates
- Use VPN for sensitive operations

---

### Threat 4: Phishing/Social Engineering
**Scenario**: User tricked into entering credentials on fake site

**Impact**:
- ❌ User's exchange account compromised

**Mitigation**:
- Display clear security warnings
- Educate users on phishing
- Use OAuth (reduces credential exposure)
- Implement 2FA on exchange accounts
- **Never ask for passwords/private keys**

---

### Threat 5: Malicious Dependencies
**Scenario**: Compromised Python package steals credentials

**Impact**:
- ❌ All stored credentials at risk
- ❌ Session credentials at risk during runtime

**Mitigation**:
- Pin dependency versions in `requirements.txt`
- Regular `pip audit` or `safety check`
- Review dependency changes before upgrading
- Use virtual environments
- Consider dependency scanning tools (Snyk, Dependabot)

---

### Threat 6: Insider Threat
**Scenario**: Malicious developer or admin accesses credentials

**Impact**:
- ❌ Option C: Admin can decrypt all keys
- ✅ Option A/B: No persistent access to user keys

**Mitigation**:
- Principle of least privilege
- Audit all admin actions
- Multi-person approval for sensitive operations
- Regular access reviews
- Use option A (session-only) for maximum security

---

## 6. Incident Response Plan

### If API Keys Are Compromised

#### Immediate Actions (Within 1 Hour)
1. **Revoke compromised keys** on exchange platforms immediately
2. **Rotate encryption keys** if using encrypted storage
3. **Invalidate all user sessions** - force re-authentication
4. **Disable affected integrations** temporarily
5. **Document the incident** - what, when, how discovered

#### Investigation (Within 24 Hours)
1. **Identify breach source** - logs, access patterns
2. **Determine scope** - which accounts affected
3. **Preserve evidence** - for forensics/legal
4. **Notify affected users** - transparency about breach
5. **Report to authorities** if required by law (GDPR, etc.)

#### Remediation (Within 1 Week)
1. **Patch vulnerability** that led to breach
2. **Enhance security controls** - implement additional safeguards
3. **Security audit** - third-party review
4. **Update documentation** - incident report, lessons learned
5. **User communication** - steps taken to prevent recurrence

#### Prevention (Ongoing)
1. **Regular security audits** - quarterly reviews
2. **Penetration testing** - annual tests
3. **Security training** - developer education
4. **Monitoring** - automated alerts
5. **Incident drills** - practice response procedures

---

## 7. Best Practices Summary

### ✅ DO
- Use **session-only storage** for maximum security (Option A)
- Implement **OAuth** where available (Coinbase, Kraken)
- Require **read-only API permissions** only
- **Validate all inputs** (addresses, API keys)
- Use **HTTPS** for all external requests
- **Clear sensitive data** from memory after use
- **Log security events** (without sensitive data)
- **Educate users** about API key security
- **Regular security audits**
- **Pin dependency versions**

### ❌ DON'T
- ❌ Never request **private keys** or **seed phrases**
- ❌ Never store API keys in **plaintext**
- ❌ Never commit secrets to **Git**
- ❌ Never log **full API keys** or secrets
- ❌ Never use API keys with **withdrawal permissions**
- ❌ Never trust **user input** without validation
- ❌ Never deploy without **HTTPS**
- ❌ Never ignore **security warnings**
- ❌ Never skip **security updates**

---

## 8. Recommended Implementation for MVP

### Phase 1: Session-Only (Week 1-2)
```python
# Simplest, most secure approach
- Store API keys in st.session_state only
- User re-enters keys each session
- Zero persistence risk
- Clear security model
```

### Phase 2: Optional Browser Encryption (Week 3-4)
```python
# For users who want convenience
- User provides passphrase
- Keys encrypted with passphrase-derived key
- Stored in browser localStorage
- User controls security
```

### Phase 3: OAuth Integration (Week 5-6)
```python
# For supported exchanges
- Coinbase OAuth implementation
- Kraken OAuth (if available)
- No API key storage needed
- Best UX + security
```

### Phase 4: Production (Week 7-8)
```python
# If deploying as multi-user SaaS
- Cloud KMS for master keys (AWS KMS, Google Cloud KMS)
- Encrypted database storage
- Full audit logging
- Compliance documentation
```

---

## 9. Code Example: Secure Session Management

```python
# services/security/session_manager.py
import streamlit as st
from datetime import datetime, timedelta
import secrets

class SecureSessionManager:
    """Manage secure sessions with automatic expiry"""

    SESSION_TIMEOUT = timedelta(hours=1)

    @staticmethod
    def init_session():
        """Initialize secure session"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = secrets.token_urlsafe(32)
            st.session_state.session_start = datetime.now()
            st.session_state.credentials = {}

    @staticmethod
    def is_session_valid() -> bool:
        """Check if session is still valid"""
        if 'session_start' not in st.session_state:
            return False

        elapsed = datetime.now() - st.session_state.session_start
        return elapsed < SecureSessionManager.SESSION_TIMEOUT

    @staticmethod
    def store_credential(account_id: str, api_key: str, api_secret: str):
        """Store credential in secure session"""
        if not SecureSessionManager.is_session_valid():
            raise ValueError("Session expired")

        st.session_state.credentials[account_id] = {
            'api_key': api_key,
            'api_secret': api_secret,
            'stored_at': datetime.now()
        }

    @staticmethod
    def get_credential(account_id: str) -> dict:
        """Retrieve credential from session"""
        if not SecureSessionManager.is_session_valid():
            SecureSessionManager.clear_session()
            raise ValueError("Session expired - please re-enter credentials")

        return st.session_state.credentials.get(account_id)

    @staticmethod
    def clear_session():
        """Clear all session data"""
        if 'credentials' in st.session_state:
            # Overwrite memory before deletion
            for cred_id in st.session_state.credentials:
                st.session_state.credentials[cred_id] = {'api_key': '0'*64, 'api_secret': '0'*64}

            st.session_state.credentials = {}

        st.session_state.session_id = None
        st.session_state.session_start = None

# Usage in main app
SecureSessionManager.init_session()

if not SecureSessionManager.is_session_valid():
    st.warning("⚠️ Session expired. Your credentials have been cleared for security.")
    st.button("Start New Session", on_click=SecureSessionManager.init_session)
    st.stop()
```

---

## 10. Security Comparison Matrix

| Feature | Session-Only | Browser Encrypted | Database Encrypted | OAuth | HSM |
|---------|-------------|-------------------|-------------------|-------|-----|
| **Security Level** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **User Convenience** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Implementation Complexity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Cost** | Free | Free | Free-Low | Free-Low | High |
| **Breach Risk** | None | Low | Medium | Very Low | None |
| **Multi-User Support** | No | No | Yes | Yes | Yes |
| **Auto-Refresh** | No | Yes | Yes | Yes | Yes |
| **Key Management** | N/A | User | Admin | Exchange | Dedicated |
| **Compliance Ready** | N/A | No | Maybe | Yes | Yes |

**Recommendation**: Start with **Session-Only**, add **OAuth** for Coinbase, then evaluate user demand for persistence.

---

## Final Recommendation

### For Crypto Portfolio Tracker MVP:

```
🏆 RECOMMENDED ARCHITECTURE:

1. Wallets (public addresses): No credentials needed
   - Use your own API keys for blockchain explorers
   - User only provides public address
   - Zero credential risk

2. Exchanges with OAuth (Coinbase): Use OAuth
   - No API key storage
   - Revokable access
   - Best security + UX

3. Exchanges without OAuth (Binance, etc.): Session-only storage
   - User re-enters keys each session
   - Clear security model
   - Optional: Allow user-encrypted local storage

4. Advanced (optional): User passphrase encryption
   - For users who want convenience
   - User controls passphrase
   - Browser-only storage
```

**Why this approach?**
- ✅ Minimizes security risk (no persistent credentials for most flows)
- ✅ Clear user communication (transparency about security model)
- ✅ Simple implementation (no complex key management)
- ✅ Scalable (can add encrypted storage later if users demand it)
- ✅ Compliant (minimal PII storage)

**Next Steps**:
1. Implement session-only storage (Week 1)
2. Add Coinbase OAuth (Week 2-3)
3. Add optional user-encrypted storage based on feedback (Week 4+)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-05
**Classification**: Internal - Security Architecture
**Review Schedule**: Quarterly
