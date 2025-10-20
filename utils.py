import json
import re

def read_data(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return {}

def write_data(file_path, data: dict) -> bool:
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    except Exception as e:
        print(f"Error writing data to {file_path}: {e}")
        return False

# Input validation utilities for billing form
def validate_email(email: str) -> bool:
    """Basic email validation."""
    if not email:
        return False
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def validate_name(name: str) -> bool:
    """Check that name is not empty and only contains letters and spaces."""
    return bool(name and re.match(r"^[A-Za-z\s'-]+$", name))

def validate_address(address: str) -> bool:
    """Check that address is not empty."""
    return bool(address and len(address.strip()) > 0)

def validate_country(country: str, allowed_countries=None) -> bool:
    """Check that country is in allowed list."""
    if allowed_countries is None:
        allowed_countries = ["Singapore", "Malaysia", "Indonesia", "Thailand", "Vietnam", "Philippines", "Other"]
    return country in allowed_countries

def validate_card_number(card_number: str) -> bool:
    """Basic check for 13-19 digit card number."""
    return bool(re.fullmatch(r"\d{13,19}", card_number.replace(' ', '')))

def validate_expiry_date(expiry: str) -> bool:
    """Check expiry date in MM/YY format and not expired (basic check)."""
    if not re.fullmatch(r"(0[1-9]|1[0-2])/\d{2}", expiry):
        return False
    # Optionally, add logic to check if date is not in the past
    return True

def validate_cvv(cvv: str) -> bool:
    """Check for 3 or 4 digit CVV."""
    return bool(re.fullmatch(r"\d{3,4}", cvv))

# one-click auto-populate billing info for testing
def autofill_billing_info():
    return {
        'email': 'john.doe@me.com',
        'name': 'John Doe',
        'address': '123 Main St, Springfield',
        'country': 'Singapore',
        'card_number': '4111 1111 1111 1111',
        'expiry_date': '12/25',
        'cvv': '123',
        'same_billing': True,
        'errors': {}
    }