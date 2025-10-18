import streamlit as st


class ProductItem():
    """Class representing a product item in the inventory."""
    _stylesheet_loaded = False  # Class variable to track if stylesheet is loaded
    
    def __init__(self, id: str, name: str, price: float, quantity: int, description: str, category: str):
        self.id = id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.description = description
        self.category = category
        self.image_url = None
        self.load_stylesheet()

    def load_stylesheet(self, css_file='styles.css'):
        # Only load stylesheet once per session
        if not ProductItem._stylesheet_loaded:
            try:
                with open(css_file) as f:
                    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
                ProductItem._stylesheet_loaded = True
            except FileNotFoundError:
                st.warning("Stylesheet not found. Using default styles.")

    @property
    def is_in_stock(self):
        return self.quantity > 0
    
    def getPrice(self) -> float:
        return self.price

    def addToCart(self):
        print(f"Adding {self.name} to cart.")
        return "alert('Item added to cart!')"

    def show(self):
        product_card = st.container(
            border=True,
        )
        card_btn = "Add to Cart"
        if self.is_in_stock:
            with product_card:
                if self.image_url:
                    st.image(self.image_url, width=150)
                st.subheader(self.name)
                st.write(self.description)
                st.write(f"**Price:** ${self.price:.2f}")
                st.write(f"**Category:** {self.category}")
                st.write(f"**Stock:** {self.quantity}")
                if st.button(
                    card_btn,
                    key=self.id,
                    icon=":material/add:",
                    width="stretch",
                    type="primary"
                ):
                    card_btn = "Added!"
                    st.rerun()
                    self.addToCart()

            # st.html(f"""
            # <div class="product-card">
            #     <h3>{self.name}</h3>
            #     <p>{self.description}</p>
            #     <p class="price">${self.price:.2f}</p>
            #     <p class="stock">{self.quantity}</p>
            #     <button onClick="{self.addToCart()}">Add to Cart</button>
            # </div>
            # """)
            # # st.write(f"**{self.name}** - ${self.price:.2f}")
            # # st.write(f"_{self.description}_")
            # # st.write(f"Category: {self.category}")
            # # st.write(f"Stock: {self.quantity}")
        else:
            # st.html(f"""
            # <div class="product-card out-of-stock">
            #     <h3>{self.name}</h3>
            #     <p>{self.description}</p>
            #     <p class="price">${self.price:.2f}</p>
            #     <p class="out-of-stock">Out of Stock</p>
            #     <button disabled>Add to Cart</button>
            # </div>
            # """)
            # # st.write(f"**{self.name}** - ${self.price:.2f}")
            # # st.write(f"_{self.description}_")
            # # st.write(f"Category: {self.category}")
            # # st.write("**Out of Stock**")
            # if self.image_url:
            #     st.image(self.image_url, width=150)
            with product_card:
                if self.image_url:
                    st.image(self.image_url, width=150)
                st.header(self.name)
                st.write(self.description)
                st.write(f"**Price:** ${self.price:.2f}")
                st.write(f"**Category:** {self.category}")
                st.error("Out of Stock", icon="⚠️")



    def __repr__(self):
        return f"Product(id={self.id}, name={self.name}, price={self.price}, stock={self.quantity}, description={self.description}, category={self.category})"