import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict
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
            st.session_state.accounts = []

    @staticmethod
    def is_session_valid() -> bool:
        """Check if session is still valid"""
        if 'session_start' not in st.session_state:
            return False

        elapsed = datetime.now() - st.session_state.session_start
        return elapsed < SecureSessionManager.SESSION_TIMEOUT

    @staticmethod
    def store_credential(account_id: str, api_key: str, api_secret: str):
        """Store credential in secure session (memory only)"""
        if not SecureSessionManager.is_session_valid():
            raise ValueError("Session expired")

        st.session_state.credentials[account_id] = {
            'api_key': api_key,
            'api_secret': api_secret,
            'stored_at': datetime.now()
        }

    @staticmethod
    def get_credential(account_id: str) -> Optional[Dict]:
        """Retrieve credential from session"""
        if not SecureSessionManager.is_session_valid():
            SecureSessionManager.clear_session()
            return None

        return st.session_state.credentials.get(account_id)

    @staticmethod
    def clear_session():
        """Clear all session data securely"""
        if 'credentials' in st.session_state:
            # Overwrite memory before deletion
            for cred_id in st.session_state.credentials:
                st.session_state.credentials[cred_id] = {
                    'api_key': '0' * 64,
                    'api_secret': '0' * 64
                }

            st.session_state.credentials = {}

        st.session_state.session_id = None
        st.session_state.session_start = None
        st.session_state.accounts = []

    @staticmethod
    def clear_all_credentials():
        """Clear all credentials from session"""
        if 'credentials' in st.session_state:
            # Overwrite memory before deletion
            for cred_id in st.session_state.credentials:
                st.session_state.credentials[cred_id] = {
                    'api_key': '0' * 64,
                    'api_secret': '0' * 64
                }
            st.session_state.credentials = {}

    @staticmethod
    def get_session_info() -> Dict:
        """Get session information for display"""
        if not SecureSessionManager.is_session_valid():
            return {'active': False}

        elapsed = datetime.now() - st.session_state.session_start
        remaining = SecureSessionManager.SESSION_TIMEOUT - elapsed

        return {
            'active': True,
            'session_id': st.session_state.session_id[:8] + '...',
            'elapsed_minutes': int(elapsed.total_seconds() / 60),
            'remaining_minutes': int(remaining.total_seconds() / 60),
            'credential_count': len(st.session_state.credentials)
        }
