import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time

# Page configuration
st.set_page_config(
    page_title="Crypto Portfolio Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    .wallet-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    .exchange-card {
        border: 1px solid #4CAF50;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f1f8e9;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'accounts' not in st.session_state:
    st.session_state.accounts = []
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# Mock data (replace with real API calls)
MOCK_WALLET_DATA = {
    'ethereum': {
        'native': {'symbol': 'ETH', 'balance': 2.5, 'price': 2400},
        'tokens': [
            {'symbol': 'USDC', 'balance': 1500, 'price': 1},
            {'symbol': 'UNI', 'balance': 100, 'price': 8.5},
            {'symbol': 'LINK', 'balance': 50, 'price': 15}
        ]
    },
    'bitcoin': {
        'native': {'symbol': 'BTC', 'balance': 0.15, 'price': 45000}
    },
    'polygon': {
        'native': {'symbol': 'MATIC', 'balance': 1000, 'price': 0.8},
        'tokens': [{'symbol': 'USDT', 'balance': 800, 'price': 1}]
    }
}

MOCK_EXCHANGE_DATA = {
    'coinbase': [
        {'symbol': 'BTC', 'balance': 0.25, 'price': 45000},
        {'symbol': 'ETH', 'balance': 3.2, 'price': 2400},
        {'symbol': 'USDC', 'balance': 5000, 'price': 1},
        {'symbol': 'SOL', 'balance': 45, 'price': 95}
    ],
    'binance': [
        {'symbol': 'BTC', 'balance': 0.1, 'price': 45000},
        {'symbol': 'ETH', 'balance': 1.8, 'price': 2400},
        {'symbol': 'BNB', 'balance': 15, 'price': 320},
        {'symbol': 'USDT', 'balance': 2500, 'price': 1}
    ],
    'kraken': [
        {'symbol': 'BTC', 'balance': 0.05, 'price': 45000},
        {'symbol': 'ETH', 'balance': 0.8, 'price': 2400},
        {'symbol': 'ADA', 'balance': 1000, 'price': 0.45}
    ]
}

# Conversion rates for different base currencies
CONVERSION_RATES = {
    'USD': {'ETH': 2400, 'BTC': 45000, 'SOL': 95, 'BNB': 320, 'ADA': 0.45, 'MATIC': 0.8, 'USDC': 1, 'USDT': 1, 'UNI': 8.5, 'LINK': 15},
    'EUR': {'ETH': 2200, 'BTC': 41000, 'SOL': 87, 'BNB': 292, 'ADA': 0.41, 'MATIC': 0.73, 'USDC': 0.91, 'USDT': 0.91, 'UNI': 7.8, 'LINK': 13.7},
    'BTC': {'ETH': 0.053, 'BTC': 1, 'SOL': 0.0021, 'BNB': 0.0071, 'ADA': 0.00001, 'MATIC': 0.000018, 'USDC': 0.000022, 'USDT': 0.000022, 'UNI': 0.00019, 'LINK': 0.00033},
    'ETH': {'ETH': 1, 'BTC': 18.75, 'SOL': 0.04, 'BNB': 0.13, 'ADA': 0.00019, 'MATIC': 0.00033, 'USDC': 0.00042, 'USDT': 0.00042, 'UNI': 0.0035, 'LINK': 0.0063}
}

def convert_price(amount, from_symbol, to_currency):
    """Convert price from one currency to another"""
    return amount * CONVERSION_RATES[to_currency].get(from_symbol, 0)

def format_currency(value, currency):
    """Format currency display"""
    if currency == 'BTC':
        return f"₿{value:.8f}"
    elif currency == 'ETH':
        return f"Ξ{value:.6f}"
    elif currency == 'EUR':
        return f"€{value:,.2f}"
    else:
        return f"${value:,.2f}"

def fetch_wallet_data(address, chain):
    """Mock function to fetch wallet data - replace with real API calls"""
    time.sleep(1)  # Simulate API delay
    return MOCK_WALLET_DATA.get(chain, {'native': {'symbol': 'ETH', 'balance': 0, 'price': 0}, 'tokens': []})

def fetch_exchange_data(exchange, api_key, api_secret):
    """Mock function to fetch exchange data - replace with real API calls"""
    time.sleep(1.5)  # Simulate API delay
    return MOCK_EXCHANGE_DATA.get(exchange, [])

def calculate_account_total(account, base_currency):
    """Calculate total value for an account"""
    total = 0
    if account['type'] == 'wallet':
        if 'native' in account['data']:
            total += convert_price(account['data']['native']['balance'], 
                                 account['data']['native']['symbol'], base_currency)
        if 'tokens' in account['data']:
            for token in account['data']['tokens']:
                total += convert_price(token['balance'], token['symbol'], base_currency)
    elif account['type'] == 'exchange':
        for asset in account['data']:
            total += convert_price(asset['balance'], asset['symbol'], base_currency)
    return total

def calculate_total_portfolio(base_currency):
    """Calculate total portfolio value"""
    total = 0
    for account in st.session_state.accounts:
        total += calculate_account_total(account, base_currency)
    return total

# Header
st.markdown('<h1 class="main-header">💰 Crypto Portfolio Tracker</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Track your DeFi wallets and centralized exchange holdings</p>', unsafe_allow_html=True)

# Sidebar for controls
st.sidebar.header("⚙️ Settings")

# Base currency selection
base_currency = st.sidebar.selectbox(
    "Base Currency",
    ['USD', 'EUR', 'BTC', 'ETH'],
    index=0
)

# Auto-refresh toggle
auto_refresh = st.sidebar.toggle("Auto Refresh (30s)", value=False)

# Hide small balances toggle
hide_small = st.sidebar.toggle("Hide Small Balances (<$1)", value=False)

# Refresh button
if st.sidebar.button("🔄 Refresh All", type="primary"):
    with st.spinner("Refreshing all accounts..."):
        for i, account in enumerate(st.session_state.accounts):
            if account['type'] == 'wallet':
                account['data'] = fetch_wallet_data(account['address'], account['chain'])
            else:
                account['data'] = fetch_exchange_data(account['exchange'], 'api_key', 'api_secret')
            account['last_updated'] = datetime.now()
    st.session_state.last_refresh = datetime.now()
    st.rerun()

# Auto-refresh logic
if auto_refresh:
    time.sleep(30)
    st.rerun()

# Add new account section
st.sidebar.markdown("---")
st.sidebar.header("➕ Add New Account")

account_type = st.sidebar.radio("Account Type", ["DeFi Wallet", "Exchange"], key="account_type")

with st.sidebar.form("add_account"):
    account_name = st.text_input("Account Name")
    
    if account_type == "DeFi Wallet":
        chain = st.selectbox("Blockchain", ['ethereum', 'bitcoin', 'polygon', 'binance-smart-chain', 'avalanche', 'solana'])
        wallet_address = st.text_input("Wallet Address", placeholder="0x... or bc1...")
        
        if st.form_submit_button("Add Wallet", type="primary"):
            if account_name and wallet_address:
                with st.spinner("Adding wallet..."):
                    wallet_data = fetch_wallet_data(wallet_address, chain)
                    new_account = {
                        'id': len(st.session_state.accounts) + 1,
                        'type': 'wallet',
                        'name': account_name,
                        'address': wallet_address,
                        'chain': chain,
                        'data': wallet_data,
                        'last_updated': datetime.now()
                    }
                    st.session_state.accounts.append(new_account)
                    st.success("Wallet added successfully!")
                    st.rerun()
            else:
                st.error("Please fill all required fields")
    
    else:  # Exchange
        exchange = st.selectbox("Exchange", ['coinbase', 'binance', 'kraken', 'kucoin', 'bybit', 'okx'])
        api_key = st.text_input("API Key", type="password")
        api_secret = st.text_input("API Secret", type="password")
        
        st.warning("⚠️ Demo Mode: API keys are not actually used or stored securely")
        
        if st.form_submit_button("Add Exchange", type="primary"):
            if account_name and api_key and api_secret:
                with st.spinner("Connecting to exchange..."):
                    exchange_data = fetch_exchange_data(exchange, api_key, api_secret)
                    new_account = {
                        'id': len(st.session_state.accounts) + 1,
                        'type': 'exchange',
                        'name': account_name,
                        'exchange': exchange,
                        'data': exchange_data,
                        'credentials': f"{api_key[:6]}...{api_key[-4:]}",
                        'last_updated': datetime.now()
                    }
                    st.session_state.accounts.append(new_account)
                    st.success("Exchange connected successfully!")
                    st.rerun()
            else:
                st.error("Please fill all required fields")

# Main content area
if st.session_state.accounts:
    # Portfolio overview
    total_value = calculate_total_portfolio(base_currency)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "💼 Total Portfolio",
            format_currency(total_value, base_currency),
            delta=f"+{format_currency(total_value * 0.05, base_currency)} (24h)" if total_value > 0 else None
        )
    
    with col2:
        wallet_count = len([a for a in st.session_state.accounts if a['type'] == 'wallet'])
        st.metric("🏦 DeFi Wallets", wallet_count)
    
    with col3:
        exchange_count = len([a for a in st.session_state.accounts if a['type'] == 'exchange'])
        st.metric("🏢 Exchanges", exchange_count)
    
    # Portfolio composition chart
    if total_value > 0:
        st.subheader("📊 Portfolio Composition")
        
        # Prepare data for charts
        composition_data = []
        for account in st.session_state.accounts:
            account_value = calculate_account_total(account, base_currency)
            if not hide_small or account_value >= 1:
                composition_data.append({
                    'Account': account['name'],
                    'Type': account['type'].title(),
                    'Value': account_value,
                    'Percentage': (account_value / total_value) * 100
                })
        
        if composition_data:
            df_composition = pd.DataFrame(composition_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Pie chart by account
                fig_pie = px.pie(df_composition, values='Value', names='Account', 
                               title=f"Portfolio Distribution ({base_currency})",
                               color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Bar chart by type
                type_summary = df_composition.groupby('Type')['Value'].sum().reset_index()
                fig_bar = px.bar(type_summary, x='Type', y='Value',
                               title=f"Value by Account Type ({base_currency})",
                               color='Type')
                st.plotly_chart(fig_bar, use_container_width=True)
    
    # Account details
    st.subheader("💳 Account Details")
    
    for i, account in enumerate(st.session_state.accounts):
        account_total = calculate_account_total(account, base_currency)
        
        if hide_small and account_total < 1:
            continue
            
        # Account header
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            if account['type'] == 'wallet':
                st.markdown(f"### 🏦 {account['name']}")
                st.caption(f"Chain: {account['chain'].title()} • Address: {account['address'][:6]}...{account['address'][-4:]}")
            else:
                st.markdown(f"### 🏢 {account['name']}")
                st.caption(f"Exchange: {account['exchange'].title()} • API: {account.get('credentials', 'N/A')}")
        
        with col2:
            st.metric("Value", format_currency(account_total, base_currency))
        
        with col3:
            if st.button(f"🗑️ Remove", key=f"remove_{i}"):
                st.session_state.accounts.pop(i)
                st.rerun()
        
        # Account assets
        if account['type'] == 'wallet':
            assets = []
            if 'native' in account['data']:
                native = account['data']['native']
                assets.append({
                    'Symbol': native['symbol'],
                    'Balance': native['balance'],
                    'Price': format_currency(native['price'], base_currency),
                    'Value': format_currency(convert_price(native['balance'], native['symbol'], base_currency), base_currency),
                    'Type': 'Native'
                })
            
            if 'tokens' in account['data']:
                for token in account['data']['tokens']:
                    value = convert_price(token['balance'], token['symbol'], base_currency)
                    if not hide_small or value >= 1:
                        assets.append({
                            'Symbol': token['symbol'],
                            'Balance': token['balance'],
                            'Price': format_currency(token['price'], base_currency),
                            'Value': format_currency(value, base_currency),
                            'Type': 'Token'
                        })
        
        else:  # Exchange
            assets = []
            for asset in account['data']:
                value = convert_price(asset['balance'], asset['symbol'], base_currency)
                if not hide_small or value >= 1:
                    assets.append({
                        'Symbol': asset['symbol'],
                        'Balance': asset['balance'],
                        'Price': format_currency(asset['price'], base_currency),
                        'Value': format_currency(value, base_currency),
                        'Type': 'Exchange'
                    })
        
        if assets:
            df_assets = pd.DataFrame(assets)
            st.dataframe(df_assets, use_container_width=True, hide_index=True)
        else:
            st.info("No assets found or all assets below threshold")
        
        st.caption(f"Last updated: {account['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown("---")

else:
    # Empty state
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h2>🚀 Welcome to Your Crypto Portfolio Tracker!</h2>
        <p style="font-size: 1.1rem; color: #666;">
            Get started by adding your first DeFi wallet or exchange account using the sidebar.
        </p>
        <p style="color: #999;">
            📱 Connect wallets from Ethereum, Bitcoin, Polygon and more<br>
            🏢 Link exchanges like Coinbase, Binance, Kraken<br>
            📊 View everything in your preferred currency
        </p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>💡 <strong>Demo Mode:</strong> This app uses mock data. In production, integrate real APIs.</p>
        <p>⚠️ <strong>Security:</strong> Never share your private keys. Use read-only API keys only.</p>
    </div>
    """, 
    unsafe_allow_html=True
)