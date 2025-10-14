import json
from models import App
from views.Pages import AdminPage, MainPage, CheckoutPage


def load_inventory(file_path='inventory.json'):
    try:
        with open(file_path, 'r') as file:
            inventory = json.load(file)
        return inventory
    except FileNotFoundError:
        return {}

def main():
    app = App.MultiPageApp(title="My Streamlit App", icon="🚀")
    inventory = load_inventory()

    admin_page = AdminPage(inventory=inventory)
    main_page = MainPage()
    checkout_page = CheckoutPage()

    main_page.load_inventory(inventory)

    app.add_page(main_page)
    app.add_page(admin_page)
    app.add_page(checkout_page)

    # Display the app
    app.display()

if __name__ == "__main__":
    main()
