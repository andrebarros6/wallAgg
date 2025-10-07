import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from tenacity import RetryError
from services.security.session_manager import SecureSessionManager
from services.account_manager import AccountManager
from services.exchanges.supported import SupportedExchanges
from utils.formatters import format_currency, format_balance, shorten_address
from utils.error_handler import ErrorHandler

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

# Initialize session
SecureSessionManager.init_session()

# Initialize account manager
if 'account_manager' not in st.session_state:
    st.session_state.account_manager = AccountManager()

# Load accounts from database on first run
if 'accounts_loaded' not in st.session_state:
    try:
        db_accounts = st.session_state.account_manager.load_accounts_from_db()
        st.session_state.accounts = db_accounts
        st.session_state.accounts_loaded = True
    except Exception as e:
        st.session_state.accounts = []
        st.session_state.accounts_loaded = True

# Check session validity
session_info = SecureSessionManager.get_session_info()
if not session_info['active']:
    st.warning("⚠️ Session expired. Your credentials have been cleared for security.")
    if st.button("Start New Session"):
        SecureSessionManager.init_session()
        st.rerun()
    st.stop()

# Header
st.markdown('<h1 class="main-header">💰 Crypto Portfolio Tracker</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Track your DeFi wallets and centralized exchange holdings</p>', unsafe_allow_html=True)

# Sidebar for controls
st.sidebar.header("⚙️ Settings")

# Session info
st.sidebar.caption(f"🔒 Session: {session_info['remaining_minutes']} min remaining")
st.sidebar.caption(f"📊 Accounts: {len(st.session_state.accounts)}")

# Base currency selection
base_currency = st.sidebar.selectbox(
    "Base Currency",
    ['usd', 'eur', 'btc', 'eth'],
    index=0,
    format_func=lambda x: x.upper()
)

# Refresh button
if st.sidebar.button("🔄 Refresh All", type="primary"):
    with st.spinner("Refreshing all accounts..."):
        for account in st.session_state.accounts:
            try:
                # Skip if account needs credentials and doesn't have them
                if account['type'] == 'exchange':
                    credentials = SecureSessionManager.get_credential(account['id'])
                    if not credentials:
                        ErrorHandler.show_warning(f"{account['name']}: Session expired. Please re-add exchange to refresh.")
                        continue

                st.session_state.account_manager.refresh_account_data(account)
                st.session_state.account_manager.save_account_to_db(account)
            except RetryError as e:
                # Unwrap RetryError for better error messages
                if e.last_attempt and e.last_attempt.exception():
                    actual_error = str(e.last_attempt.exception())
                    ErrorHandler.show_error(f"Failed to refresh {account['name']}", actual_error)
                else:
                    ErrorHandler.show_error(f"Failed to refresh {account['name']}", "Connection failed after retries")
            except Exception as e:
                ErrorHandler.show_error(f"Failed to refresh {account['name']}", str(e))
    st.rerun()

# Clear all button
if st.sidebar.button("🗑️ Clear All", type="secondary"):
    if st.session_state.accounts:
        st.session_state.account_manager.delete_all_accounts()
        st.session_state.accounts = []
        SecureSessionManager.clear_all_credentials()
        ErrorHandler.show_success("All accounts cleared")
        st.rerun()
    else:
        ErrorHandler.show_warning("No accounts to clear")

# Add new account section
st.sidebar.markdown("---")
st.sidebar.header("➕ Add New Account")

account_type = st.sidebar.radio("Account Type", ["DeFi Wallet", "Exchange"], key="account_type")

if account_type == "DeFi Wallet":
    with st.sidebar.form("add_wallet"):
        st.markdown("### Add DeFi Wallet")
        wallet_name = st.text_input("Wallet Name", placeholder="My ETH Wallet")
        blockchain = st.selectbox("Blockchain", ['ethereum', 'bitcoin'])
        wallet_address = st.text_input(
            "Wallet Address",
            placeholder="0x... or bc1...",
            help="Only public addresses - never enter private keys!"
        )

        if st.form_submit_button("Add Wallet", type="primary"):
            if wallet_name and wallet_address:
                try:
                    with st.spinner("Adding wallet..."):
                        account = st.session_state.account_manager.add_wallet_account(
                            wallet_name, blockchain, wallet_address
                        )
                        st.session_state.account_manager.save_account_to_db(account)
                        st.session_state.accounts.append(account)
                        ErrorHandler.show_success(f"Added {wallet_name}")
                        st.rerun()
                except RetryError as e:
                    # Unwrap the RetryError to get the actual error
                    if e.last_attempt and e.last_attempt.exception():
                        actual_error = str(e.last_attempt.exception())
                        ErrorHandler.show_error("Failed to add wallet", actual_error)
                    else:
                        ErrorHandler.show_error("Failed to add wallet", "Connection failed after multiple retries")
                except ValueError as e:
                    ErrorHandler.show_error("Failed to add wallet", str(e))
                except Exception as e:
                    ErrorHandler.show_error("Failed to add wallet", f"Unexpected error: {str(e)}")
            else:
                ErrorHandler.show_error("Please fill all required fields")

else:  # Exchange
    with st.sidebar.form("add_exchange"):
        st.markdown("### Add Exchange")

        exchange_name = st.text_input("Exchange Name", placeholder="My Binance Account")
        exchange = st.selectbox(
            "Exchange",
            SupportedExchanges.get_exchange_list(),
            format_func=lambda x: SupportedExchanges.get_exchange_info(x).get('name', x)
        )

        st.warning("🔒 API keys stored in session only (cleared when you close browser)")
        st.caption("**Required permissions**: Read balances only")
        st.caption("**Forbidden**: Withdrawals, trading, transfers")

        api_key = st.text_input("API Key", type="password", help="Read-only API key")
        api_secret = st.text_input("API Secret", type="password", help="API secret")

        # Show docs link
        exchange_info = SupportedExchanges.get_exchange_info(exchange)
        if exchange_info.get('docs_url'):
            st.caption(f"[How to create API keys]({exchange_info['docs_url']})")

        if st.form_submit_button("Connect Exchange", type="primary"):
            if exchange_name and api_key and api_secret:
                try:
                    with st.spinner(f"Connecting to {exchange}..."):
                        account = st.session_state.account_manager.add_exchange_account(
                            exchange_name, exchange, api_key, api_secret
                        )
                        st.session_state.account_manager.save_account_to_db(account)
                        st.session_state.accounts.append(account)
                        ErrorHandler.show_success(f"Connected to {exchange_name}")
                        st.rerun()
                except Exception as e:
                    ErrorHandler.show_error("Failed to connect exchange", str(e))
            else:
                ErrorHandler.show_error("Please fill all required fields")

# Main content area
if st.session_state.accounts:
    # Calculate portfolio total
    total_value = 0.0
    for account in st.session_state.accounts:
        if account.get('data'):
            try:
                value = st.session_state.account_manager.calculate_account_value(account, base_currency)
                total_value += value
            except Exception as e:
                st.error(f"Error calculating value for {account.get('name', 'Unknown')}: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

    # Portfolio overview
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "💼 Total Portfolio",
            format_currency(total_value, base_currency.upper()),
            help="Total value across all accounts"
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

        composition_data = []
        for account in st.session_state.accounts:
            if account.get('data'):
                try:
                    account_value = st.session_state.account_manager.calculate_account_value(account, base_currency)
                    if account_value > 0:
                        composition_data.append({
                            'Account': account['name'],
                            'Type': account['type'].title(),
                            'Value': account_value,
                            'Percentage': (account_value / total_value) * 100
                        })
                except:
                    pass

        if composition_data:
            df_composition = pd.DataFrame(composition_data)

            col1, col2 = st.columns(2)

            with col1:
                fig_pie = px.pie(
                    df_composition,
                    values='Value',
                    names='Account',
                    title=f"Portfolio Distribution ({base_currency.upper()})",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                fig_bar = px.bar(
                    df_composition,
                    x='Account',
                    y='Value',
                    title=f"Account Values ({base_currency.upper()})",
                    color='Type',
                    text='Value'
                )
                fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                st.plotly_chart(fig_bar, use_container_width=True)

    # Account details
    st.subheader("💳 Account Details")

    for i, account in enumerate(st.session_state.accounts):
        # Check if we have data
        if not account.get('data'):
            # Try to load from cached holdings
            if account.get('cached_holdings'):
                st.info(f"ℹ️ {account['name']}: Using cached data. Click refresh to update.")
            else:
                if account['type'] == 'wallet':
                    # Try to fetch wallet data
                    try:
                        with st.spinner(f"Loading {account['name']}..."):
                            st.session_state.account_manager.refresh_account_data(account)
                    except:
                        st.warning(f"⚠️ {account['name']}: Unable to load data")
                        continue
                else:
                    st.warning(f"⚠️ {account['name']}: Session expired. Please re-add exchange.")
                    continue

        # Calculate account value
        account_total = 0.0
        try:
            account_total = st.session_state.account_manager.calculate_account_value(account, base_currency)
        except:
            pass

        # Account header
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            if account['type'] == 'wallet':
                st.markdown(f"### 🏦 {account['name']}")
                st.caption(f"Chain: {account['blockchain'].title()} • Address: {shorten_address(account['address'])}")
            else:
                st.markdown(f"### 🏢 {account['name']}")
                st.caption(f"Exchange: {account['exchange'].title()}")

        with col2:
            st.metric("Value", format_currency(account_total, base_currency.upper()))

        with col3:
            if st.button(f"🗑️ Remove", key=f"remove_{i}"):
                st.session_state.accounts.pop(i)
                st.rerun()

        # Account assets
        assets = []

        if account['type'] == 'wallet' and account.get('data'):
            if 'native' in account['data'] and account['data']['native']:
                native = account['data']['native']
                try:
                    price = st.session_state.account_manager.price_client.get_price(native['symbol'], base_currency)
                    value = native['balance'] * price if price else 0
                except:
                    price = 0
                    value = 0

                assets.append({
                    'Symbol': native['symbol'],
                    'Balance': format_balance(native['balance'], native['symbol']),
                    'Type': 'Native',
                    'Value': format_currency(value, base_currency.upper()) if value > 0 else 'N/A'
                })

            if 'tokens' in account['data']:
                for token in account['data']['tokens']:
                    try:
                        price = st.session_state.account_manager.price_client.get_price(token['symbol'], base_currency)
                        value = token['balance'] * price if price else 0
                    except:
                        price = 0
                        value = 0

                    assets.append({
                        'Symbol': token['symbol'],
                        'Balance': format_balance(token['balance'], token['symbol']),
                        'Type': 'Token',
                        'Value': format_currency(value, base_currency.upper()) if value > 0 else 'N/A'
                    })

        elif account['type'] == 'exchange' and account.get('data'):
            for asset in account['data']:
                try:
                    price = st.session_state.account_manager.price_client.get_price(asset['symbol'], base_currency)
                    value = asset['balance'] * price if price else 0
                except:
                    price = 0
                    value = 0

                assets.append({
                    'Symbol': asset['symbol'],
                    'Balance': format_balance(asset['balance'], asset['symbol']),
                    'Type': 'Exchange',
                    'Value': format_currency(value, base_currency.upper()) if value > 0 else 'N/A'
                })

        if assets:
            df_assets = pd.DataFrame(assets)
            st.dataframe(df_assets, use_container_width=True, hide_index=True)
        else:
            st.info("No assets found")

        if account.get('last_updated'):
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
            📱 Connect wallets from Ethereum, Bitcoin<br>
            🏢 Link exchanges like Coinbase, Binance, Kraken<br>
            📊 View everything in your preferred currency<br>
            🔒 Session-only security - keys never saved
        </p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>🔒 <strong>Security:</strong> API keys stored in session memory only • Cleared on browser close</p>
        <p>⚠️ <strong>Important:</strong> Never share your private keys or seed phrases</p>
    </div>
    """,
    unsafe_allow_html=True
)
