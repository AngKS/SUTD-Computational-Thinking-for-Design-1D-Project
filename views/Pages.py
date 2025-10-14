import streamlit as st
from models.Page import Page
from models.Product import ProductItem
from models.Transaction import Transaction

class AdminPage(Page):
    _logged_in = False
    def __init__(self, inventory=None):
        super().__init__(title="Admin", icon="🛠️")
        self.inventory = inventory if inventory is not None else []

    @property
    def logged_in(self):
        return AdminPage._logged_in
    @logged_in.setter
    def logged_in(self, value: bool):
        AdminPage._logged_in = value

    def login_form(self):
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if username == "admin" and password == "admin123":  # Replace with secure check
                    self.logged_in = True
                    st.success("Logged in successfully!")
                    st.rerun()  # Refresh the page to show admin content
                else:
                    st.error("Invalid credentials. Please try again.")

    def inventory_management(self):
        st.header("Inventory Management")
        # create a dataframe from inventory
        if not self.inventory:
            st.info("No inventory data available.")
            return
        df = st.dataframe(self.inventory["products"])



    def display(self):
        # super().display()
        st.write("This is the Admin page where transactions are handled.")
        if not self.logged_in:
            st.warning("Please log in to access admin features.")
            self.login_form()
        else:
            st.write("Welcome, Admin! Here you can manage transactions.")
            self.inventory_management()


class CheckoutPage(Page):
    def __init__(self, transaction: Transaction = None):
        super().__init__(title="Checkout", icon="🛒")
        self.transaction = transaction

    def display(self):
        st.title(f"{self.icon} {self.title}")
        
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
    def __init__(self):
        super().__init__(title="Main", icon="🏠")

    @property
    def products(self):
        return self._products if hasattr(self, '_products') else []

    def load_inventory(self, inventory):
        # check for counts and load products
        self._products = [ProductItem(**item) for item in inventory["products"]]

    def display(self):
        # super().display()
        st.write("Welcome to the Main Page of the application!")
        st.write("Use the sidebar to navigate to different sections.")
        
        # Show product grid (mobile: single column, desktop: multi-column)
        cols = st.columns(3)  # Adjust number of columns as needed
        for i, product in enumerate(self.products):
            with cols[i % 3]:  # Change 3 to the number of columns
                product.show()


