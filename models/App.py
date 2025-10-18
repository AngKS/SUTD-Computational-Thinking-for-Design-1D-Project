import streamlit as st
from models.Page import Page

class MultiPageApp:
    """Main application class to manage pages and navigation."""
    def __init__(self, title: str, icon: str = "🌐"):
        self.title = title
        self.icon = icon
        self.pages = []
        self.layout = "wide"

    def add_page(self, page: Page):
        """Add a new page to the application."""
        self.pages.append(page)

    def goto_page(self, page_title: str):
        """Navigate to a specific page by title."""
        # Update session state to trigger navigation
        if 'current_page' not in st.session_state:
            st.session_state.current_page = page_title
        else:
            st.session_state.current_page = page_title
        st.rerun()

    def display(self):
        """Display the application with navigation."""
        st.set_page_config(
            page_title=self.title,
            page_icon=self.icon,
            layout=self.layout
        )
        st.image("assets/banner.png")
        # Initialize session state for current page
        if 'current_page' not in st.session_state:
            st.session_state.current_page = self.pages[0].title

        # Navigation navbar
        page_titles = [f"{page.icon} {page.title}" for page in self.pages]
        current_page_with_icon = f"{self._get_page_icon(st.session_state.current_page)} {st.session_state.current_page}"
        col1, col3 = st.columns([3, 1])
        with col1:
            selected_page = st.segmented_control(
                "",
                page_titles,
                default=current_page_with_icon,
                label_visibility="hidden"
            )

            # Extract title without icon
            selected_title = selected_page.split(" ", 1)[1]

            # Update session state if page changed
            if selected_title != st.session_state.current_page:
                st.session_state.current_page = selected_title
                st.rerun()
        with col3:
            st.button(
                "Cart",
                icon=":material/shopping_cart:",
            )

        # Display the current page
        for page in self.pages:
            if page.title == st.session_state.current_page:
                page.display()
                break

    def _get_page_icon(self, page_title: str) -> str:
        """Helper method to get the icon for a page by title."""
        for page in self.pages:
            if page.title == page_title:
                return page.icon
        return "📄"
