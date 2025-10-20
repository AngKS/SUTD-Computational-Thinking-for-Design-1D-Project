from models import App, Transaction
from views.AdminPage import AdminPage
from views.MainPage import MainPage
from views.CheckoutPage import CheckoutPage
import uuid
from datetime import datetime as dt
import streamlit as st
# Application Launcher

def main():
    app = App.MultiPageApp(title="KSMD Store", icon="./assets/KSMD Logo.png")
    
    # Initialize transaction only if it doesn't exist
    if 'transaction' not in st.session_state:
        st.session_state.transaction = Transaction.Transaction(transaction_id = str(uuid.uuid4()), date = dt.now().strftime("%Y-%m-%d %H:%M:%S"))

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
