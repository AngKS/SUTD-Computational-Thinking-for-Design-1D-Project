import streamlit as st


class ProductItem():
    def __init__(self, id, name, price, quantity, description, category, image):
        self.id = id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.description = description
        self.category = category
        self.image = image
        self.load_stylesheet()

    def load_stylesheet(self, css_file='styles.css'):
        try:
            with open(css_file) as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except FileNotFoundError:
            st.warning("Stylesheet not found. Using default styles.")

    @property
    def is_in_stock(self):
        return self.quantity > 0

    def addToCart(self):
        """Add this product to the cart with stock validation"""
        if 'transaction' in st.session_state:
            transaction = st.session_state.transaction
            success, amount = transaction.addItem(self, quantity=1)

            if success:
                # Successfully added to cart
                st.toast(f"✅ {self.name} added to cart!", icon="🛒")
            else:
                # Maximum stock already in cart
                st.toast(f"❌ Sorry! Max limit reached ({self.quantity} in stock)", icon="🛑")
        else:
            st.error("Transaction not initialized!")

    def show(self):
        if self.is_in_stock:
            st.image(self.image)

            # Display product info using HTML for styling
            st.html(f"""
                <div class="product-card">
                    <h3 class="product-name">{self.name}</h3>
                    <p class="product-description">{self.description}</p>
                    <p class="product-price">${self.price:.2f}</p>
                    <p class="product-stock">In Stock: {self.quantity}</p>
                </div>
            """)

            # Add functional Streamlit button with custom styling
            if st.button(
                    "🛒 Add to Cart",
                    key=f"add_to_cart_{self.id}",
                    on_click=self.addToCart,
                    use_container_width=True,
                    type="primary"
            ):
                pass  # Action handled by on_click callback

        else:
            st.image(self.image)
            st.html(f"""
                <div class="product-card">
                    <h3 class="product-name">{self.name}</h3>
                    <p class="product-description">{self.description}</p>
                    <p class="product-price">${self.price:.2f}</p>
                    <p class="product-out-of-stock">Out of Stock</p>
                </div>
            """)
