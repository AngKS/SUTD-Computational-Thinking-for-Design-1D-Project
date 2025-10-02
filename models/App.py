import streamlit as st

class MultiPageApp:
    """Main application class to manage pages and navigation."""
    def __init__(self, title: str, icon: str = "🌐"):
        self.title = title
        self.icon = icon
        self.pages = []

    def add_page(self, page):
        """Add a new page to the application."""
        self.pages.append(page)

    def display(self):
        """Display the application with navigation."""
        st.set_page_config(page_title=self.title, page_icon=self.icon)
        st.title(f"{self.icon} {self.title}")

        # Navigation sidebar
        page_titles = [f"{page.icon} {page.title}" for page in self.pages]
        selected_page = st.sidebar.selectbox("Navigate to", page_titles)

        # Display the selected page
        for page in self.pages:
            if f"{page.icon} {page.title}" == selected_page:
                page.display()
                break
    def run(self):
        page = st.sidebar.selectbox(
            "Welcome to the App! Select a page:",
            [f"{page.icon} {page.title}" for page in self.pages],
            format_func=lambda x: x.split(" ", 1)[1]  # Display only the title in the dropdown
        )
        page.display()

    def __str__(self):
        return f"App(title={self.title}, icon={self.icon}, pages={len(self.pages)})"
    
    def __repr__(self):
        return self.__str__()