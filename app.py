from models import App
from views.AdminPage import AdminPage
from views.MainPage import MainPage
from views.CheckoutPage import CheckoutPage


def main():
    app = App.MultiPageApp(title="My Streamlit App", icon="🚀")

    admin_page = AdminPage(app)
    main_page = MainPage(app)
    checkout_page = CheckoutPage(app)

    app.add_page(main_page)
    app.add_page(admin_page)
    app.add_page(checkout_page)

    # Display the app
    app.display()

if __name__ == "__main__":
    main()
