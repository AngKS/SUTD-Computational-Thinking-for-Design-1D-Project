import streamlit as st
from models.Page import Page
from models.App import MultiPageApp
from models.Product import ProductItem
from utils import read_data

class MainPage(Page):
    def __init__(self, _app: MultiPageApp):
        super().__init__(title="Shop", icon="🏪")
        self.app = _app
        self._products = [ProductItem(**item) for item in read_data('inventory.json').get('products', [])]

    @property
    def products(self):
        return self._products if hasattr(self, '_products') else []

    def display(self):
        # super().display()
        st.write("Welcome to the Main Page of the application!")
        st.write("Use the sidebar to navigate to different sections.")

        # Show product grid (mobile: single column, desktop: multi-column)
        cols = st.columns(3)  # Adjust number of columns as needed
        for i, product in enumerate(self.products):
            with cols[i % 3]:  # Change 3 to the number of columns
                product.show()


