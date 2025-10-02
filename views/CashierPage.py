import streamlit as st
from models.Page import Page

class CashierPage(Page):
    def __init__(self):
        super().__init__(title="Cashier", icon="💰")

    def display(self):
        # super().display()
        st.write("This is the Cashier page where transactions are handled.")
        # Add more cashier-specific functionality here