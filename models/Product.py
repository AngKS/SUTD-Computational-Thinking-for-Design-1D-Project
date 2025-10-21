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

    @staticmethod
    def load_stylesheet(css_file='styles.css'):
        """Load stylesheet - should be called once per rerun in app.py"""
        try:
            with open(css_file) as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except FileNotFoundError:
            st.warning("Stylesheet not found. Using default styles.")

    @property
    def is_in_stock(self):
        return self.quantity > 0
    
    def getPrice(self) -> float:
        return self.price

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
        product_card = st.container(border=True)
        
        with product_card:
            # Add responsive wrapper for mobile/desktop layouts
            st.html(f"""
                <div class="product-wrapper" id="product-{self.id}">
            """)
            
            # Create horizontal layout using columns with responsive spec
            # On mobile, columns will stack automatically
            col1, col2 = st.columns([1, 2], gap="medium")
            
            with col1:
                # Display product image using Streamlit's native image component
                st.image(self.image, use_container_width=True)
            
            with col2:
                # Display product details
                if self.is_in_stock:
                    st.html(f"""
                        <div class="product-details">
                            <h3 class="product-name">{self.name}</h3>
                            <p class="product-description">{self.description}</p>
                            <p class="product-price">${self.price:.2f}</p>
                            <p class="product-stock">In Stock: {self.quantity}</p>
                        </div>
                    """)
                else:
                    st.html(f"""
                        <div class="product-details">
                            <h3 class="product-name">{self.name}</h3>
                            <p class="product-description">{self.description}</p>
                            <p class="product-price">${self.price:.2f}</p>
                            <p class="product-out-of-stock">Out of Stock</p>
                        </div>
                    """)
            
            st.html("</div>")  # Close product-wrapper
            
            # Add functional Streamlit button with custom styling (only for in-stock items)
            if self.is_in_stock:
                if st.button(
                        "Add to Cart",
                        icon=":material/add:",
                        key=f"add_to_cart_{self.id}",
                        on_click=self.addToCart,
                        use_container_width=True,
                        type="primary"
                ):
                    pass  # Action handled by on_click callback
