import streamlit as st
from models.Page import Page
from models.App import MultiPageApp
from models.Transaction import Transaction


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