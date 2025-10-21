import streamlit as st
import ast


class ProductItem():

    def __init__(self, id, name, price, quantity, description, category, image, 
                 base_price=None, pricing_metadata=None):
        self.id = id
        self.name = name
        self.base_price = base_price if base_price is not None else price  # Original price before dynamic adjustments
        self.price = price  # Current effective price (displayed to customers)
        self.quantity = quantity
        self.description = description
        self.category = category
        self.image = image
        
        # Handle pricing_metadata - convert string to dict if needed
        if isinstance(pricing_metadata, str):
            try:
                self.pricing_metadata = ast.literal_eval(pricing_metadata)
            except (ValueError, SyntaxError):
                self.pricing_metadata = {}
        elif isinstance(pricing_metadata, dict):
            self.pricing_metadata = pricing_metadata
        else:
            self.pricing_metadata = {}
            
        # pricing_metadata structure:
        # {
        #     'popularity_tier': 'trending',
        #     'popularity_score': 7,
        #     'pricing_multiplier': 1.05,
        #     'badges': ['🔥 HOT ITEM'],
        #     'last_updated': '2025-10-21'
        # }

    @staticmethod
    def load_stylesheet(css_file='styles.css'):
        """Load CSS stylesheet - called once per page render.
        
        Streamlit doesn't persist st.markdown() CSS across st.rerun(),
        so we need to inject it on every render. We use a unique key
        to prevent Streamlit from warning about duplicate elements.
        """
        try:
            with open(css_file) as f:
                # Use st.markdown with a container to ensure CSS is injected on every rerun
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except FileNotFoundError:
            st.warning("Stylesheet not found. Using default styles.")

    @property
    def is_in_stock(self):
        return self.quantity > 0
    
    def getPrice(self) -> float:
        return self.price
    
    def getBasePrice(self) -> float:
        """Get the original base price before dynamic pricing"""
        return self.base_price
    
    def getPriceChangePercentage(self) -> float:
        """Return percentage difference from base price"""
        if self.base_price and self.base_price > 0:
            return ((self.price - self.base_price) / self.base_price) * 100
        return 0.0
    
    def hasPriceChanged(self) -> bool:
        """Check if current price differs from base price"""
        return abs(self.price - self.base_price) > 0.01
    
    def getPopularityTier(self) -> str:
        """Return current popularity tier"""
        return self.pricing_metadata.get('popularity_tier', 'normal')
    
    def getDiscountBadges(self) -> list:
        """Return list of discount/promotion badges for UI display"""
        return self.pricing_metadata.get('badges', [])

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
            
            # Create horizontal layout using columns with responsiveness
            # On mobile, columns will stack automatically
            col1, col2 = st.columns([1, 2], gap="medium")
            
            with col1:
                # Display product image using Streamlit's native image component
                st.image(self.image, use_container_width=True)
            
            with col2:
                # Display product details
                if self.is_in_stock:
                    # Get pricing badges
                    badges_html = ""
                    for badge in self.getDiscountBadges():
                        badges_html += f'<span class="product-badge">{badge}</span> '
                    
                    # Show price with base price comparison if changed
                    price_html = ""
                    if self.hasPriceChanged():
                        change_percent = self.getPriceChangePercentage()
                        if change_percent < 0:  # Discount
                            price_html = f'''
                                <p class="product-price">
                                    <span style="text-decoration: line-through; color: #888; font-size: 0.9em;">${self.base_price:.2f}</span>
                                    <span style="color: #28a745; font-weight: bold;"> ${self.price:.2f}</span>
                                    <span style="color: #28a745; font-size: 0.85em;"> (Save {abs(change_percent):.0f}%)</span>
                                </p>
                            '''
                        else:  # Premium pricing
                            price_html = f'''
                                <p class="product-price">
                                    <span style="color: #dc3545; font-weight: bold;">${self.price:.2f}</span>
                                    <span style="color: #888; font-size: 0.85em;"> (was ${self.base_price:.2f})</span>
                                </p>
                            '''
                    else:
                        price_html = f'<p class="product-price">${self.price:.2f}</p>'
                    
                    st.html(f"""
                        <div class="product-details">
                            <h3 class="product-name">{self.name}</h3>
                            {badges_html}
                            <p class="product-description">{self.description}</p>
                            {price_html}
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
            
            st.html("</div>")
            
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
            else:
                st.button(
                    "Out of Stock",
                    icon=":material/block:",
                    key=f"out_of_stock_{self.id}",
                    disabled=True,
                    use_container_width=True,
                    type="secondary"
                )
                
