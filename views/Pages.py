import streamlit as st
from models.Page import Page
from models.Product import ProductItem

class CashierPage(Page):
    def __init__(self):
        super().__init__(title="Cashier", icon="💰")

    def display(self):
        # super().display()
        st.write("This is the Cashier page where transactions are handled.")
        # Add more cashier-specific functionality here


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


