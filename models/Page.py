import streamlit as st

# Parent or base class, basic structure and properties other pages inherit from.

class Page:
    """Base class for application pages."""
    def __init__(self, title: str, icon: str = "📄"):
        self.title = title
        self.icon = icon

    def display(self):
        st.set_page_config(page_title=self.title, page_icon=self.icon)
        # st.title(f"{self.icon} {self.title}")
        # st.write(f"Welcome to the {self.title} page!")

    def __str__(self):
        return f"Page(title={self.title}, icon={self.icon})"
    
    def __repr__(self):
        return self.__str__()


