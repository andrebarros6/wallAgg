import streamlit as st
from typing import Callable
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling"""

    @staticmethod
    def handle_api_error(func: Callable) -> Callable:
        """Decorator for API error handling"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    st.error("⚠️ Rate limit exceeded. Please wait a moment and try again.")
                elif e.response.status_code == 401:
                    st.error("🔐 Authentication failed. Please check your API keys.")
                else:
                    st.error(f"❌ API error: {str(e)}")
                logger.error(f"API error in {func.__name__}: {e}")
                return None
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                return None
        return wrapper

    @staticmethod
    def show_error(message: str, details: str = None):
        """Display user-friendly error"""
        st.error(f"❌ {message}")
        if details:
            with st.expander("Error Details"):
                st.code(details)

    @staticmethod
    def show_warning(message: str):
        """Display warning"""
        st.warning(f"⚠️ {message}")

    @staticmethod
    def show_success(message: str):
        """Display success message"""
        st.success(f"✅ {message}")

    @staticmethod
    def show_info(message: str):
        """Display info message"""
        st.info(f"ℹ️ {message}")
