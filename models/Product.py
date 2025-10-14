import streamlit as st


class ProductItem():
    """Class representing a product item in the inventory."""
    def __init__(self, id, name, price, quantity, description, category):
        self.id = id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.description = description
        self.category = category
        self.image_url = None
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
        print(f"Adding {self.name} to cart.")
        return "alert('Item added to cart!')"

    def show(self):
        if self.is_in_stock:
            st.html(f"""
            <div class="product-card">
                <h3>{self.name}</h3>
                <p>{self.description}</p>
                <p class="price">${self.price:.2f}</p>
                <p class="stock">{self.quantity}</p>
                <button onClick="{self.addToCart}">Add to Cart</button>
            </div>
            """)
            # st.write(f"**{self.name}** - ${self.price:.2f}")
            # st.write(f"_{self.description}_")
            # st.write(f"Category: {self.category}")
            # st.write(f"Stock: {self.quantity}")
        else:
            st.html(f"""
            <div class="product-card out-of-stock">
                <h3>{self.name}</h3>
                <p>{self.description}</p>
                <p class="price">${self.price:.2f}</p>
                <p class="out-of-stock">Out of Stock</p>
                <button disabled>Add to Cart</button>
            </div>
            """)
            # st.write(f"**{self.name}** - ${self.price:.2f}")
            # st.write(f"_{self.description}_")
            # st.write(f"Category: {self.category}")
            # st.write("**Out of Stock**")
            if self.image_url:
                st.image(self.image_url, width=150)
            

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name}, price={self.price}, stock={self.quantity}, description={self.description}, category={self.category})"