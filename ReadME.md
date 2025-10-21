# 10.025 Computational Thinking for Design - 1D Project
![Project Banner](assets/banner.png)

## Project Overview
A PC hardware e-commerce web application built with Streamlit, featuring custom multi-page navigation, AI-powered analytics, shopping cart functionality, and comprehensive admin controls.

## Core Features

| Feature | Description | Implementation |
|---------|-------------|----------------|
| **Custom Navigation** | Segmented control-based page routing with session state management | [`models/App.py`](models/App.py) |
| **Product Catalog** | Responsive grid layout with custom HTML/CSS cards, stock status, and real-time pricing | [`models/Product.py`](models/Product.py), [`views/MainPage.py`](views/MainPage.py) |
| **Shopping Cart** | Full cart management with item quantity controls and live total calculations | [`models/Transaction.py`](models/Transaction.py) |
| **Secure Checkout** | Validated billing forms with autofill, promo code support, and order confirmation | [`views/CheckoutPage.py`](views/CheckoutPage.py) |
| **Admin Panel** | Tabbed dashboard for inventory, transactions, and AI analytics | [`views/AdminPage.py`](views/AdminPage.py) |
| **AI Analytics** ⚡ | Natural language queries with auto-generated charts and metrics (GPT-4o-mini) | [`services/ai_query_service.py`](services/ai_query_service.py) |
| **JSON Persistence** | File-based data storage for inventory, transactions, and promo codes | [`utils.py`](utils.py) |
| **SHA-256 Auth** | Secure admin authentication with session management | [`auth.py`](auth.py) |

## Feature Details

### 🛒 Shopping Experience
- **Stock Validation**: Real-time inventory checks prevent overselling
- **Promo Codes**: Multiple discount codes (`SUMMER10`, `WELCOME15`, `FREESHIP`)
- **Smart Autofill**: One-click billing form population for testing
- **Form Validation**: Regex-based validation for email, card numbers, CVV, and expiry dates

### 🛠️ Admin Features
| Feature | Capability | Access |
|---------|------------|--------|
| **Inventory Editor** | Add/edit/delete products with live data editor | Admin Tab |
| **Transaction Viewer** | Search by ID, customer, country; export to CSV | Admin Tab |
| **AI Dashboard** | Query sales data using natural language | Dashboard Tab |
| **Promo Manager** | View and manage discount codes | Admin Tab |

### 🤖 AI Analytics (Optional)
- **Natural Language Queries**: "Show top 5 products by revenue"
- **Auto Visualizations**: Generates metrics, charts, dataframes from GPT responses
- **Component Types**: `metric`, `bar_chart`, `line_chart`, `dataframe`, `markdown`
- **Setup**: Requires OpenAI API key in `.env` file (see [AI_ANALYTICS_README.md](AI_ANALYTICS_README.md))

## Quick Start

### Prerequisites
| Requirement | Version | Installation |
|-------------|---------|--------------|
| Python | 3.12+ | [python.org](https://python.org) |
| UV Package Manager | Latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` (macOS/Linux)<br>`powershell -c "irm https://astral.sh/uv/install.ps1 \| iex"` (Windows) |

### Setup & Run
```bash
# 1. Clone repository
git clone <repository-url>
cd SUTD-Computational-Thinking-for-Design-1D-Project

# 2. Create virtual environment
uv venv env
source env/bin/activate  # Windows: env\Scripts\activate

# 3. Install dependencies
uv pip install -r requirements.txt

# 4. (Optional) Configure AI Analytics
cp .env.example .env
# Add OPENAI_API_KEY to .env

# 5. Run application
streamlit run app.py
```

## Tech Stack
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | Streamlit 1.50.0 | Web application framework |
| **Data Processing** | Pandas 2.3.3, NumPy 2.3.3 | Data manipulation and analysis |
| **Visualization** | Matplotlib 3.10.6, Altair 5.5.0 | Charts and graphs |
| **AI Integration** | OpenAI 1.54.5 | GPT-4o-mini for analytics |
| **Persistence** | JSON | File-based data storage |
| **Authentication** | SHA-256 | Password hashing |

## Project Structure
```
├── app.py                 # Application entry point
├── models/                # Data models (App, Page, Product, Transaction)
├── views/                 # Page implementations (Admin, Main, Checkout)
├── services/              # AI analytics services
├── utils.py               # Utilities (validation, JSON I/O)
├── auth.py                # Authentication module
├── config.py              # Configuration (AI settings)
├── *.json                 # Data files (inventory, transactions, promocodes)
└── assets/                # Images, static files, and AI prompts
    └── prompts/           # GPT system prompts and schemas
```

## Testing Credentials
| Account | Username | Password | Access |
|---------|----------|----------|--------|
| Admin | `admin` | Created on first login | Full admin panel access |

**Test Promo Codes**: `SUMMER10` (10% off), `WELCOME15` (15% off), `FREESHIP` (free shipping)

## Group Members
| Name | Student ID |
|------|------------|
| Ang Kah Shin | 1009929 |
| Maxwell Lee | TBD |
| Dishanta Mohanty | TBD |

## Documentation
- **AI Analytics Guide**: [AI_ANALYTICS_README.md](AI_ANALYTICS_README.md)

## References
- [Streamlit Dynamic Navigation](https://docs.streamlit.io/develop/tutorials/multipage/dynamic-navigation)
- [OpenAI API Documentation](https://platform.openai.com/docs)

---
*Course: 10.025 Computational Thinking for Design | SUTD*