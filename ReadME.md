# 10.025 Computational Thinking for Design - 1D Project

This repository contains the code and resources for the 1D Project of the 10.025 Computational Thinking for Design course at SUTD.

## Project Overview

This is a PC hardware e-commerce web application built with Streamlit. The application features a custom multi-page navigation system, product catalog management, shopping cart functionality, and an admin panel for inventory control.

## Key Features

| Feature | Description | Link to Feature Implementation |
|---------|-------------|-------------------------------|
| **Custom Multi-Page Navigation** | Dynamic page routing system using segmented controls instead of Streamlit's default sidebar navigation | [`models/App.py`](models/App.py) |
| **Product Catalog Display** | Responsive grid layout showing PC hardware products with custom HTML/CSS cards, stock status, and pricing | [`models/Product.py`](models/Product.py), [`views/Pages.py#L155-177`](views/Pages.py#L155-177) |
| **Inventory Management** | Interactive data editor for adding, updating, and removing products with real-time JSON persistence | [`views/Pages.py#L58-77`](views/Pages.py#L58-77) |
| **Secure Admin Authentication** | SHA-256 password hashing with session-based login/logout functionality | [`auth/app.py`](auth/app.py) |
| **Shopping Cart & Checkout** | Cart management with billing form, order summary, and discount code support | [`views/Pages.py#L115-152`](views/Pages.py#L115-152) |
| **Transaction Processing** | Transaction object model with tax calculation and discount application | [`models/Transaction.py`](models/Transaction.py) |
| **JSON Data Persistence** | File-based storage system for inventory and transaction data without database dependencies | [`views/Pages.py#L8-20`](views/Pages.py#L8-20) |
| **Stock Status Tracking** | Real-time inventory tracking with out-of-stock indicators and quantity display | [`models/Product.py#L27-29`](models/Product.py#L27-29) |
| **Singleton CSS Loading** | Optimized stylesheet loading pattern to prevent duplicate CSS injection on reruns | [`models/Product.py#L5-24`](models/Product.py#L5-24) |
| **Admin Dashboard** | Tabbed interface for managing inventory, viewing transactions, and monitoring system status | [`views/Pages.py#L95-113`](views/Pages.py#L95-113) |

## Project Requirements:
- **Good Programming Practices**
- **Python Features**
- **Algorithms learnt**
- **Flexibility to Changes**

## Project Prerequisites
- Python 3.x installed on your machine.
- Python UV package/project manager installed (Install via pip: `pip install uv`).
```bash
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
- Basic knowledge of Python programming.
- Familiarity with command line interface.


## Project Setup
1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Setup a virtual environment (optional but recommended).
   ```bash
   uv venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```
4. Install the required dependencies.
    ```bash
    uv pip install -r requirements.txt
    ```
5. Run the main script to start the project.
    ```bash
    streamlit run app.py
    ```

## Project dependencies
```plaintext
streamlit
numpy
matplotlib
pandas
```


## Group Members information
- Ang Kah Shin (1009929)
- Maxwell Lee ()
- Dishanta Mohanty ()


### Notes
- https://docs.streamlit.io/develop/tutorials/multipage/dynamic-navigation