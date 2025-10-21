from models import App, Transaction
from views.AdminPage import AdminPage
from views.MainPage import MainPage
from views.CheckoutPage import CheckoutPage
from datetime import datetime as dt
import streamlit as st
from services.pricing_engine import PricingEngine
from utils import read_data, write_data
import os

# Application Launcher

def update_prices_on_startup():
    """
    Automatically update product prices on application startup
    This runs once per session using session state tracking
    """
    # Check if prices have already been updated in this session
    if 'prices_updated' in st.session_state:
        return
    
    try:
        # Check if required files exist
        if not os.path.exists('inventory.json'):
            st.warning("⚠️ inventory.json not found - skipping price update")
            st.session_state.prices_updated = True
            return
        
        if not os.path.exists('pricing_config.json'):
            # No pricing config, skip update silently
            st.session_state.prices_updated = True
            return
        
        # Load inventory data
        inventory_data = read_data('inventory.json')
        if not inventory_data or 'products' not in inventory_data:
            st.session_state.prices_updated = True
            return
        
        # Load transactions
        if os.path.exists('transactions.json'):
            txn_data = read_data('transactions.json')
            transactions = txn_data.get('transactions', [])
        else:
            transactions = []
        
        # Initialize pricing engine
        engine = PricingEngine()
        
        # Create lightweight product objects for price calculation
        class SimpleProduct:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
                if not hasattr(self, 'base_price') or self.base_price is None:
                    self.base_price = self.price
                if not hasattr(self, 'pricing_metadata'):
                    self.pricing_metadata = {}
        
        products = [SimpleProduct(**p_data) for p_data in inventory_data['products']]
        
        # Update prices
        stats = engine.update_all_prices(products, transactions)
        
        # Save updated prices back to inventory
        for i, product in enumerate(products):
            inventory_data['products'][i]['price'] = product.price
            inventory_data['products'][i]['base_price'] = product.base_price
            inventory_data['products'][i]['pricing_metadata'] = product.pricing_metadata
        
        write_data('inventory.json', inventory_data)
        
        # Mark as updated and show notification if changes were made
        st.session_state.prices_updated = True
        
        # Optional: Show subtle notification if prices changed
        if stats['prices_changed'] > 0:
            st.toast(f"✨ {stats['prices_changed']} product prices updated!", icon="💰")
        
    except Exception as e:
        # Silently fail - don't break the app if price update fails
        print(f"Price update error: {e}")
        st.session_state.prices_updated = True


def main():
    app = App.MultiPageApp(title="KSMD Store", icon="./assets/KSMD Logo.png")
    
    # Update prices on startup (runs once per session)
    update_prices_on_startup()
    
    # Initialize transaction only if it doesn't exist using factory method
    if 'transaction' not in st.session_state:
        st.session_state.transaction = Transaction.Transaction.create_new_transaction()

    admin_page = AdminPage(app)
    main_page = MainPage(app)
    checkout_page = CheckoutPage(app)

    app.add_page(main_page)
    app.add_page(admin_page)
    app.add_page(checkout_page)

    # Display the app
    app.display()

if __name__ == "__main__":
    main()
