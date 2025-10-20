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

    def load_inventory(self, inventory):
        self._products = [ProductItem(**item) for item in inventory["products"]]

    def display(self):
        # st.image("Images/KSMD Logo.png")
        # st.write("Use the sidebar to navigate to different sections.")
        # Show product grid
        cols = st.columns(3)

        for i, product in enumerate(self.products):
            with cols[i % 3]:
                product.show()