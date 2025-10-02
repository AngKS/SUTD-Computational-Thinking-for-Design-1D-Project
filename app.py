from models import App


def main():
    app = App.MultiPageApp(title="My Streamlit App", icon="🚀")

    # Add pages to the app
    from models.Page import Page

    home_page = Page(title="Home", icon="🏠")
    about_page = Page(title="About", icon="ℹ️")
    contact_page = Page(title="Contact", icon="📞")

    app.add_page(home_page)
    app.add_page(about_page)
    app.add_page(contact_page)

    # Display the app
    app.display()

if __name__ == "__main__":
    main()
