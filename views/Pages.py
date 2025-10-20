import streamlit as st
from models.Page import Page
from models.Product import ProductItem
from models.Transaction import Transaction


class CashierPage(Page):
    def __init__(self):
        super().__init__(title="Cashier", icon="💰")
        # Initialize transaction in session state if not exists
        if 'transaction' not in st.session_state:
            st.session_state.transaction = Transaction(transaction_id=1)

    def display(self):
        st.title("🛒 Shopping Cart")

        transaction = st.session_state.transaction

        if transaction.isEmpty():
            st.info("Your cart is empty. Go to the Main page to add products!")
            return

        # Display cart items
        for product_id, item_data in transaction.cart_items.items():
            product = item_data['product']
            quantity = item_data['quantity']
            subtotal = transaction.getSubtotal(product_id)

            col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 2, 1])

            with col1:
                st.image(product.image, width=100)

            with col2:
                st.write(f"**{product.name}**")
                st.write(product.description[:50] + "...")

            with col3:
                st.write(f"**Price:** ${product.price:.2f}")

            with col4:
                st.write(f"**Quantity:** {quantity}")
                st.write(f"**Subtotal:** ${subtotal:.2f}")

            with col5:
                if st.button("🗑️", key=f"remove_{product_id}"):
                    transaction.removeItemCompletely(product_id)
                    st.rerun()
                if st.button("➕", key=f"add_{product_id}"):
                    transaction.addItem(product, quantity=1)
                    st.rerun()
                if st.button("➖", key=f"subtract_{product_id}"):
                    transaction.removeItem(product_id, quantity=1)
                    st.rerun()

            st.divider()

        # Display total
        st.subheader(f"**Total: ${transaction.getTotal():.2f}**")
        st.write(f"Total Items: {transaction.getItemCount()}")

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Cart", type="secondary"):
                transaction.clearCart()
                st.rerun()

        with col2:
            if st.button("Checkout", type="primary"):
                st.success("Order placed successfully!")
                transaction.clearCart()
                st.rerun()


class MainPage(Page):
    def __init__(self):
        super().__init__(title="Main", icon="🏠")
        # Initialize transaction in session state if not exists
        if 'transaction' not in st.session_state:
            st.session_state.transaction = Transaction(transaction_id=1)

    @property
    def products(self):
        return self._products if hasattr(self, '_products') else []

    def load_inventory(self, inventory):
        self._products = [ProductItem(**item) for item in inventory["products"]]

    def display(self):
        st.image("Images/KSMD Logo.png")
        # st.write("Use the sidebar to navigate to different sections.")

        # Show product grid
        cols = st.columns(3)

        for i, product in enumerate(self.products):
            with cols[i % 3]:
                product.show()