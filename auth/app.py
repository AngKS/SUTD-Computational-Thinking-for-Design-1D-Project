import streamlit as st
import hashlib
import os






def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_file: str = 'password') -> bool:
    """
    Verify password against stored hash.
    If password file doesn't exist, create it with the hash of the provided password.
    """
    if not os.path.exists(password_file):
        # No password file exists
        hashed = hash_password(password)
        with open(password_file, 'w') as f:
            f.write(hashed)
        return True
    else:
        # Password file exists
        with open(password_file, 'r') as f:
            stored_hash = f.read().strip()
        return hash_password(password) == stored_hash


def login(username: str, password: str) -> bool:
    """
    Authenticate user and save the login state in Streamlit session.
    Returns True if authentication successful, False otherwise.
    """
    if username == "admin" and verify_password(password):
        # Use Streamlit's session state to establish login
        st.session_state["_auth_user"] = {"username": username, "role": "admin"}
        return True
    return False

def logout():
    """
    Logout user and clear session state.
    """
    if "_auth_user" in st.session_state:
        del st.session_state["_auth_user"]
        return True


def is_logged_in() -> bool:
    """
    Check if user is currently logged in using Streamlit session
    """
    return st.session_state.get("_auth_user") is not None


def get_current_user():
    """
    Get current logged in user information
    """
    return st.session_state.get("_auth_user")
