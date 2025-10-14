import json
from models import App
from views.Pages import CashierPage, MainPage


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

    cashier_page = CashierPage()
    main_page = MainPage()

    main_page.load_inventory(inventory)

    app.add_page(main_page)
    app.add_page(cashier_page)

    # Display the app
    app.display()

if __name__ == "__main__":
    main()
