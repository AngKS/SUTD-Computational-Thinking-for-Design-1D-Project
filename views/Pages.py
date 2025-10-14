import streamlit as st
import json
from models.Page import Page
from models.App import MultiPageApp
from models.Product import ProductItem
from models.Transaction import Transaction
from auth import app as auth

def read_data(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return {}

def write_data(file_path, data: dict) -> bool:
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
        return True
    return False


class AdminPage(Page):
    def __init__(self, _app: MultiPageApp):
        super().__init__(title="Admin", icon="🛠️")
        self.app = _app
        self.transactions = read_data('transactions.json')
        self.inventory = read_data('inventory.json')

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
            
            tab1, tab2, tab3 = st.tabs(["Dashboard", "Transactions", "Inventory"])
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

class CheckoutPage(Page):
    def __init__(self, _app: MultiPageApp, transaction: Transaction = None):
        super().__init__(title="Cart", icon="🛒")
        self.app = _app
        self.transaction = transaction

    def display(self):
        st.title(f"{self.icon} {self.title}")
        if self.transaction is None:
            st.warning("You currently have no items in your cart.", icon="⚠️")
            if st.button("Go back to shop"):
                self.app.goto_page("Shop")
            return
        col1, col2 = st.columns([3, 1])
        with col1:
            with st.form("cart_form"):
                st.header("Billing Information")
                st.text_input("Full Name")
                st.text_input("Email Address")
                st.text_input("Phone Number")
                st.text_area("Shipping Address")
                st.form_submit_button("Submit", width="stretch")
        with col2:
            st.header("Order Summary")
            cart_items = st.expander("View Cart Items", expanded=False)
            with cart_items:
                if self.transaction is None or not self.transaction.products:
                    st.error("Your cart is empty.", icon="⚠️")
                else:
                    for products in self.transaction.products:
                        st.write(f"{products.name} - ${products.getPrice():.2f}")
                        st.markdown("---")

            st.write("Item 1: $10.00")
            st.write("Item 2: $15.00")
            st.write("Total: $25.00")
            # discount code section
            st.text_input("Discount Code", placeholder="Enter code here")
class MainPage(Page):
    def __init__(self, _app: MultiPageApp):
        super().__init__(title="Shop", icon="🏪")
        self.app = _app
        self._products = [ProductItem(**item) for item in read_data('inventory.json').get('products', [])]

    @property
    def products(self):
        return self._products if hasattr(self, '_products') else []

    def display(self):
        # super().display()
        st.write("Welcome to the Main Page of the application!")
        st.write("Use the sidebar to navigate to different sections.")

        # Show product grid (mobile: single column, desktop: multi-column)
        cols = st.columns(3)  # Adjust number of columns as needed
        for i, product in enumerate(self.products):
            with cols[i % 3]:  # Change 3 to the number of columns
                product.show()


