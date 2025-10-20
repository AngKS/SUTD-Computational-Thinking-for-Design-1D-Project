import streamlit as st
from models.Page import Page
from models.App import MultiPageApp
from models.Transaction import Transaction

# Import validation functions
from utils import (
    validate_email, validate_name, validate_address, validate_country,
    validate_card_number, validate_expiry_date, validate_cvv, autofill_billing_info
)


class CheckoutPage(Page):
    def __init__(self, _app: MultiPageApp = None):
        super().__init__(title="Cart", icon="🛒")
        self.app = _app

    def billing_info(self):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.subheader("Billing Information")
        with col2:
            if st.button("Autofill from Profile", icon=":material/badge:"):
                autofill_data = autofill_billing_info()
                # Store autofill data in session state
                for key, value in autofill_data.items():
                    st.session_state[f'billing_{key}'] = value
                st.rerun()
        
        errors = {}
        
        # Use session state values if available
        email = st.text_input("Email Address", value = st.session_state.get('billing_email', ''))
        if email and not validate_email(email):
            errors['email'] = "Invalid email address."
        
        st.write("Shipping information")
        name = st.text_input("Name", value = st.session_state.get('billing_name', ''))
        if name and not validate_name(name):
            errors['name'] = "Invalid name. Only letters, spaces, hyphens, and apostrophes allowed."
        
        address = st.text_area("Address", value = st.session_state.get('billing_address', ''))
        if address and not validate_address(address):
            errors['address'] = "Address cannot be empty."
        
        country_options = ["Singapore", "Malaysia", "Indonesia", "Thailand", "Vietnam", "Philippines", "Other"]
        default_country_index = 0
        if 'billing_country' in st.session_state:
            try:
                default_country_index = country_options.index(st.session_state['billing_country'])
            except ValueError:
                default_country_index = 0
        country = st.selectbox("Country", options = country_options, index = default_country_index)
        if country and not validate_country(country, allowed_countries=country_options):
            errors['country'] = "Invalid country selection."
        
        st.subheader("Payment Details")
        card_number = st.text_input("Card Number", value = st.session_state.get('billing_card_number', ''))
        if card_number and not validate_card_number(card_number):
            errors['card_number'] = "Invalid card number. Must be 13-19 digits."
        
        col1, col2 = st.columns(2)
        with col1:
            expiry_date = st.text_input("Expiry Date (MM/YY)", value = st.session_state.get('billing_expiry_date', ''))
            if expiry_date and not validate_expiry_date(expiry_date):
                errors['expiry_date'] = "Invalid expiry date. Use MM/YY."
        with col2:
            cvv = st.text_input("CVV", type = "password", value = st.session_state.get('billing_cvv', ''))
            if cvv and not validate_cvv(cvv):
                errors['cvv'] = "Invalid CVV. Must be 3 or 4 digits."
        
        same_billing = st.checkbox("Billing address is the same as shipping address", value = st.session_state.get('billing_same_billing', False))

        # Show errors inline
        for field, msg in errors.items():
            st.error(f"{msg}")

        # Return all values and errors for use in checkout
        return {
            'email': email,
            'name': name,
            'address': address,
            'country': country,
            'card_number': card_number,
            'expiry_date': expiry_date,
            'cvv': cvv,
            'same_billing': same_billing,
            'errors': errors
        }

    def discount_code(self, transaction: Transaction = None):
        # read promocodes from file
        code = st.text_input("Discount Code (optional)")
        apply_btn = st.button("Apply Code")
        
        if apply_btn and code:
            if transaction.applyPromoCode(code):
                st.success("Discount code applied!")
                st.balloons()
                st.rerun()
            else:
                st.error("Invalid promo code. Please try again.")
        elif apply_btn and not code:
            st.warning("Please enter a promo code.")
        
        # Show currently applied promo code if any
        if transaction.promo_code:
            st.info(f"Active discount: {transaction.promo_code['discount_percent']}% off (Code: {transaction.promo_code['code']})")


    def display(self):

        transaction = st.session_state.transaction
        st.subheader("Transaction ID: " + transaction.transaction_id)
        st.divider()

        if transaction.isEmpty():
            st.info("Your cart is empty. Go to the Main page to add products!")
            return
        else:
            col1, col2 = st.columns([3, 1])
            with col1:
                # Billing address, payment info with validation
                billing = self.billing_info()

            with col2:
                st.write("Total payable amount:")
                st.title(f"${transaction.getTotal():.2f}")
                st.divider()
                with st.expander(f"View Cart Details ({transaction.getItemCount()})"):
                    # Display cart items
                    for product_id, item_data in transaction.cart_items.items():
                        product = item_data['product']
                        quantity = item_data['quantity']
                        subtotal = transaction.getProductSubtotal(product_id)

                        col1, col2= st.columns([2, 3])

                        with col1:
                            st.image(product.image, width=100)

                        with col2:
                            itemHeader1, itemHeader2 = st.columns([4, 1])
                            with itemHeader1:
                                st.write(f"**{product.name}**")
                            with itemHeader2:
                                if st.button("🗑️", key=f"remove_{product_id}"):
                                    transaction.removeItemCompletely(product_id)
                                    st.rerun()
                            st.write(product.description[:50] + "...")
                        sub_col1, subcol2, subcol3 = st.columns([3, 1, 1])
                        with sub_col1:
                            st.write(f"**Quantity:** {quantity}")
                        with subcol2:
                            if st.button("➕", key=f"add_{product_id}"):
                                transaction.addItem(product, quantity=1)
                                st.rerun()
                        with subcol3:
                            if st.button("➖", key=f"subtract_{product_id}"):
                                transaction.removeItem(product_id, quantity=1)
                                st.rerun()
                        st.write(f"**Price:** ${product.price:.2f}")

                        st.write(f"**Subtotal:** ${subtotal:.2f}")

                        st.divider()

                # Display total
                st.write(f"Subtotal: {transaction.getSubTotal():.2f}")
                st.subheader(f"**Total: ${transaction.getTotal():.2f}**")
                self.discount_code(transaction=transaction)

                checkout_btn = st.button("Checkout", type="primary", use_container_width=True)
                if checkout_btn:
                    # Validate all fields are filled and no errors
                    required_fields = ['email', 'name', 'address', 'country', 'card_number', 'expiry_date', 'cvv']
                    missing = [f for f in required_fields if not billing[f]]
                    if missing:
                        st.error("Please fill in all required fields.")
                    elif billing['errors']:
                        st.error("Please correct the errors above before checking out.")
                    else:
                        st.success("Order placed successfully!")
                        transaction.clearCart()
                        st.rerun()