import streamlit as st
from models.Page import Page
from models.App import MultiPageApp
from utils import read_data, write_data
import auth

class AdminPage(Page):
    def __init__(self, _app: MultiPageApp):
        super().__init__(title="Admin", icon="🛠️")
        self.app = _app
        self.transactions = read_data('transactions.json')
        self.inventory = read_data('inventory.json')
        self.promocodes = read_data('promocodes.json')

    @property
    def logged_in(self):
        """Check if user is logged in using auth module"""
        return auth.is_logged_in()

    def login_form(self):
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if auth.login(username, password):
                    st.success("Logged in successfully!")
                    st.rerun()  # Refresh the page to show admin content
                else:
                    st.error("Invalid credentials. Please try again.")

    def logout_button(self):
        """Display logout button"""
        if st.button("Logout", key="admin_logout"):
            auth.logout()
            st.success("Logged out successfully!")
            st.rerun()


    def inventory_management(self):
        st.header("Inventory Management")
        # create a dataframe from inventory
        if not self.inventory:
            st.info("No inventory data available.")
            return
        df = st.data_editor(self.inventory["products"])
        # check for changes and update inventory
        if df != self.inventory["products"]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info("Changes detected in inventory.")
            with col2:
                if st.button("Save Changes"):
                    self.inventory["products"] = df
                    success = write_data('inventory.json', self.inventory)
                    if success:
                        st.success("Inventory updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update inventory.")

    def transaction_management(self):
        st.header("Transaction Management")
        if not self.transactions:
            st.info("No transaction data available.")
            return
        df = st.data_editor(self.transactions["transactions"])
        if st.button("Save Transaction Changes"):
            self.transactions["transactions"] = df.to_dict(orient="records")
            write_data('transactions.json', self.transactions)
            st.success("Transactions updated successfully!")

    def promocode_management(self):
        st.header("Promotional Code Management")
        if not self.promocodes:
            st.info("No promotional code data available.")
            return
        df = st.data_editor(self.promocodes["codes"])
        if df != self.promocodes["codes"]:
            if st.button("Save Promo Code Changes"):
                self.promocodes["codes"] = df
                write_data('promocodes.json', self.promocodes)
                st.success("Promotional codes updated successfully!")

    def display(self):
        if not self.logged_in:
            st.warning("Please log in to access admin features.")
            self.login_form()
        else:
            # Display logout button in sidebar or at top
            col1, col2 = st.columns([5, 1])
            with col1:
                st.title("Admin Panel")
            with col2:
                self.logout_button()
            
            tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Transactions", "Inventory", "Discount Codes"])
            with tab1:
                st.write("Welcome to the Admin Dashboard!")
                st.write("Use the tabs to navigate through different admin features.")
                user_info = auth.get_current_user()
                if user_info:
                    st.info(f"Logged in as: {user_info.get('username', 'Unknown')}")
            with tab2:
                self.transaction_management()
            with tab3:
                self.inventory_management()
            with tab4:
                self.promocode_management()
