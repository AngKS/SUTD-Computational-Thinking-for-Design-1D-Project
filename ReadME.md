# 10.025 Computational Thinking for Design - 1D Project
![Project Banner](assets/banner.png)

This repository contains the code and resources for the 1D Project of the 10.025 Computational Thinking for Design course at SUTD.

## 📋 Project Overview

**KSMD Store** is a fully-featured PC hardware e-commerce web application built with Streamlit. The application implements a custom multi-page navigation system, comprehensive product catalog management, intelligent shopping cart functionality with stock validation, and a secure admin panel for complete inventory and transaction control—all without requiring a database.

## ✨ Key Features

### 🛒 Customer Features

| Feature | Description | Implementation |
|---------|-------------|----------------|
| **Custom Multi-Page Navigation** | Dynamic page routing system using segmented controls instead of Streamlit's default sidebar navigation, providing a modern, app-like experience | [`models/App.py`](models/App.py) |
| **Product Catalog Display** | Responsive 3-column grid layout showcasing PC hardware products with custom HTML/CSS cards, real-time stock status indicators, and dynamic pricing | [`models/Product.py`](models/Product.py), [`views/MainPage.py`](views/MainPage.py) |
| **Intelligent Shopping Cart** | Real-time cart management with stock validation, quantity controls (add/remove individual items), and per-product subtotal calculations | [`models/Transaction.py`](models/Transaction.py) |
| **Stock Validation System** | Prevents over-ordering by validating cart quantities against available inventory with user-friendly toast notifications | [`models/Product.py`](models/Product.py) |
| **Promotional Code System** | Apply discount codes at checkout with percentage-based discounts automatically calculated in order totals | [`models/Transaction.py`](models/Transaction.py), [`views/CheckoutPage.py`](views/CheckoutPage.py) |
| **Comprehensive Checkout Flow** | Multi-step billing form with shipping information, payment details, and complete order review before purchase | [`views/CheckoutPage.py`](views/CheckoutPage.py) |
| **Form Validation** | Real-time validation for email, name, address, card number (13-19 digits), CVV (3-4 digits), and expiry date (MM/YY format) using regex patterns | [`utils.py`](utils.py) |
| **Auto-fill Testing Feature** | One-click "Autofill from Profile" button pre-populates billing form with test data for rapid development and testing | [`utils.py`](utils.py) |
| **Transaction ID System** | Unique transaction IDs generated with timestamp format (TXN20251021143052) for order tracking | [`models/Transaction.py`](models/Transaction.py) |

### 🛠️ Admin Features

| Feature | Description | Implementation |
|---------|-------------|----------------|
| **Secure Admin Authentication** | SHA-256 password hashing with session-based authentication, automatic password file creation on first login | [`auth.py`](auth.py) |
| **Admin Dashboard** | Comprehensive overview with key metrics: total transactions, total revenue, and average order value | [`views/AdminPage.py`](views/AdminPage.py) |
| **Inventory Management** | Interactive Streamlit data editor for adding, updating, and removing products with change detection and real-time JSON persistence | [`views/AdminPage.py`](views/AdminPage.py) |
| **Transaction Management** | Complete transaction history with search/filter capabilities by transaction ID, customer email, name, or country | [`views/AdminPage.py`](views/AdminPage.py) |
| **Transaction Details View** | Expandable transaction cards showing customer info, itemized purchases, promo codes applied, and total amounts | [`views/AdminPage.py`](views/AdminPage.py) |
| **Transaction Deletion** | Safe deletion with confirmation dialog to prevent accidental data loss | [`views/AdminPage.py`](views/AdminPage.py) |
| **CSV Export Feature** | Export all transaction data to CSV format with flattened structure for analysis in Excel or other tools | [`views/AdminPage.py`](views/AdminPage.py) |
| **Promotional Code Management** | Edit existing promo codes or add new ones with percentage discount values using interactive data editor | [`views/AdminPage.py`](views/AdminPage.py) |
| **Tabbed Interface** | Organized admin panel with separate tabs for Dashboard, Transactions, Inventory, and Discount Codes | [`views/AdminPage.py`](views/AdminPage.py) |

### 🏗️ Technical Features

| Feature | Description | Implementation |
|---------|-------------|----------------|
| **JSON Data Persistence** | File-based storage system for inventory, transactions, and promo codes—no database required | [`utils.py`](utils.py) |
| **Singleton CSS Loading** | Optimized stylesheet loading pattern called once per rerun in `app.py` to prevent duplicate CSS injection across page navigation | [`models/Product.py`](models/Product.py) |
| **Session State Management** | Streamlit session state used for transaction object, current page tracking, admin authentication, and billing form autofill | [`app.py`](app.py) |
| **Factory Pattern** | Transaction objects created via factory method `create_new_transaction()` ensuring consistent ID generation and timestamp initialization | [`models/Transaction.py`](models/Transaction.py) |
| **Object-Oriented Design** | Clean separation of concerns with Page base class, Product items, Transaction management, and App controller | [`models/`](models/) |
| **Responsive Layout** | Mobile-friendly design with responsive columns that stack on smaller screens | [`models/Product.py`](models/Product.py) |
| **Custom Page System** | Pages inherit from base `Page` class with `title` and `icon` properties; navigation requires explicit `st.rerun()` to trigger re-render | [`models/Page.py`](models/Page.py) |

## 🚀 Getting Started

### Prerequisites
- **Python 3.12+** installed on your machine
- **pip** package manager
- Basic knowledge of Python programming
- Familiarity with command line interface

### Installation Options

#### Option 1: Using UV (Recommended)
UV is a fast Python package installer and resolver. Install it first:
```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then set up the project:
```bash
# Clone the repository
git clone <repository-url>
cd SUTD-Computational-Thinking-for-Design-1D-Project

# Create and activate virtual environment
uv venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

#### Option 2: Using Standard pip
```bash
# Clone the repository
git clone <repository-url>
cd SUTD-Computational-Thinking-for-Design-1D-Project

# Create and activate virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Ensure virtual environment is activated
source env/bin/activate  # On Windows: env\Scripts\activate

# Start the Streamlit application
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## 🧪 Testing & Development

### Quick Testing with Auto-fill
1. Navigate to the Cart page
2. Add products to cart from the Shop page
3. Click "Autofill from Profile" button to populate form with test data:
   - **Email**: john.doe@me.com
   - **Name**: John Doe
   - **Address**: 123 Main St, Springfield
   - **Country**: Singapore
   - **Card**: 4111 1111 1111 1111
   - **Expiry**: 12/25
   - **CVV**: 123

### Test Promo Codes
Try these promotional codes at checkout:
- `SUMMER10` - 10% discount
- `WELCOME15` - 15% discount

(Check `promocodes.json` for all available codes)

### Admin Access
- **Username**: `admin`
- **Password**: Set on first login (hashed in `password` file using SHA-256)
- Default location: Project root directory

## 📁 Project Structure

```
.
├── app.py                      # Application entry point & initialization
├── auth.py                     # Authentication module with SHA-256 hashing
├── utils.py                    # Utility functions (validation, JSON I/O, autofill)
├── styles.css                  # Custom CSS for product cards & layout
├── requirements.txt            # Python dependencies
│
├── models/                     # Core business logic
│   ├── App.py                 # Custom multi-page navigation system
│   ├── Page.py                # Base class for all pages
│   ├── Product.py             # ProductItem class with cart integration
│   └── Transaction.py         # Shopping cart & transaction management
│
├── views/                      # UI pages
│   ├── MainPage.py            # Product catalog (Shop page)
│   ├── CheckoutPage.py        # Shopping cart & billing form
│   └── AdminPage.py           # Admin panel with 4 tabs
│
├── assets/                     # Static assets
│   ├── banner.png             # Application header banner
│   └── KSMD Logo.png          # Store logo
│
├── Images/                     # Product images
│   └── *.png                  # Product photos referenced in inventory.json
│
├── Data Files (JSON)
│   ├── inventory.json         # Product catalog
│   ├── transactions.json      # Transaction history
│   ├── promocodes.json        # Discount codes
│   └── password               # Admin password hash (auto-generated)
│
└── env/                        # Virtual environment (not in git)
```

## 🗂️ Data File Structures

### inventory.json
```json
{
  "products": [
    {
      "id": "prod001",
      "name": "Gaming Graphics Card",
      "price": 599.99,
      "quantity": 15,
      "description": "High-performance GPU",
      "category": "Graphics Cards",
      "image": "Images/gpu.png"
    }
  ]
}
```

### promocodes.json
```json
{
  "codes": [
    {
      "code": "SUMMER10",
      "discount_percent": 10,
      "description": "10% summer discount"
    }
  ]
}
```

### transactions.json
```json
{
  "transactions": [
    {
      "transaction_id": "TXN20251021143052",
      "date": "2025-10-21 14:30:52",
      "customer": {
        "email": "customer@example.com",
        "name": "John Doe",
        "address": "123 Main St",
        "country": "Singapore"
      },
      "items": [
        {
          "product_id": "prod001",
          "name": "Gaming Graphics Card",
          "price": 599.99,
          "quantity": 1
        }
      ],
      "promo_code": {"code": "SUMMER10", "discount_percent": 10},
      "total_amount": 539.99
    }
  ]
}
```

## 📦 Dependencies

Core dependencies (see [`requirements.txt`](requirements.txt) for complete list):

```plaintext
streamlit==1.50.0          # Web application framework
pandas==2.3.3              # Data manipulation & admin data editor
numpy==2.3.3               # Numerical operations
matplotlib==3.10.6         # Data visualization (if needed)
```

Full dependency list includes supporting libraries for JSON schema validation, date handling, and Streamlit's internal requirements.

## 🔧 Configuration & Customization

### Adding New Products
**Via Admin Panel (Recommended)**:
1. Login to Admin panel
2. Navigate to "Inventory" tab
3. Use data editor to add/edit products
4. Click "Save Changes"

**Manual Edit**:
Edit `inventory.json` directly with required fields:
- `id`: Unique product identifier
- `name`: Product name
- `price`: Price in dollars
- `quantity`: Stock quantity
- `description`: Product description
- `category`: Product category
- `image`: Path to product image (relative to project root)

### Adding Promo Codes
**Via Admin Panel**:
1. Login to Admin panel
2. Navigate to "Discount Codes" tab
3. Add new row or edit existing codes
4. Save changes

**Manual Edit**:
Edit `promocodes.json`:
```json
{
  "codes": [
    {"code": "NEWCODE20", "discount_percent": 20, "description": "20% discount"}
  ]
}
```

### Modifying Validation Rules
Edit validation functions in [`utils.py`](utils.py):
- `validate_email()` - Email regex pattern
- `validate_card_number()` - Card length (currently 13-19 digits)
- `validate_cvv()` - CVV length (currently 3-4 digits)
- `validate_expiry_date()` - Date format and expiry check

### Customizing Appearance
Edit [`styles.css`](styles.css) to modify:
- Product card styling
- Color schemes
- Layout spacing
- Responsive breakpoints

## 👥 Team Members

- **[Ang Kah Shin](https://github.com/angks)** (1009929)
- **[Maxwell Lee](https://github.com/G3N3SYS1)** (1010639)
- **[Dishanta Mohanty](https://github.com/dishantamohanty)** (1010935)


## 📚 References & Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Multi-page Apps](https://docs.streamlit.io/develop/tutorials/multipage/dynamic-navigation)
- [Python Regular Expressions](https://docs.python.org/3/library/re.html)
- [JSON in Python](https://docs.python.org/3/library/json.html)


## 📄 License
This project is created for educational purposes as part of SUTD's 10.025 Computational Thinking for Design course.

---

**Note**: This application uses file-based JSON storage and is intended for educational purposes. For production use, consider implementing a proper database system, secure payment processing, and enhanced security measures.