<div align="center">

# 🍽️ Restaurant Management System

**A premium, multi-role desktop application built with PyQt6 and MS SQL Server**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![SQL Server](https://img.shields.io/badge/MS_SQL_Server-2022-CC2927?style=for-the-badge&logo=microsoftsqlserver&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

<br/>

*A full-scale enterprise desktop application for managing multi-branch restaurant operations — orders, inventory, billing, kitchen display, staff, and more.*

</div>

---

## 👥 Team — Group 6

> **BS Artificial Intelligence — Bahria University, Karachi Campus**

| Member | GitHub |
|--------|--------|
| Huzaifa | [@huzaifa](https://github.com/huzaifa206) |
| Irteza  | [@irteza](https://github.com/mirteza1010-blip) |
| Faizan  | [@faizan](https://github.com/faizan-github-username) |

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Running the App](#-running-the-app)
- [User Roles & Credentials](#-user-roles--credentials)
- [Database Schema](#-database-schema)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)

---

## 🧠 Overview

The **Restaurant Management System (RMS)** is a small-scale enterprise-level desktop application designed to manage multiple restaurant branches from a centralized platform. It integrates all major restaurant operations into a single, cohesive interface built using **PyQt6** with a custom dark-mode design system (*Obsidian & Ember*) and backed by **Microsoft SQL Server**.

This system is ideal for restaurant chains, franchises, and food businesses that need a unified tool for daily operations.

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 🔐 **Role-Based Login** | 6 distinct roles with isolated dashboards and access control |
| 📋 **Order Management** | Dine-in, takeaway, and online orders with real-time status tracking |
| 🍛 **Menu Management** | Add, edit, toggle availability, and manage categories |
| 📦 **Inventory Tracking** | Stock monitoring with low-stock alerts and reorder levels |
| 🧾 **Billing & Invoicing** | Auto-calculated invoices with 17% GST and payment recording |
| 👨‍🍳 **Kitchen Display (KDS)** | Live auto-refreshing order queue for kitchen staff |
| 👥 **Staff Management** | Employee records, roles, salaries, and activation control |
| 🪑 **Table Management** | Visual table grid with live status (Available / Occupied / Reserved) |
| 🚚 **Supplier Portal** | Supplier-facing panel to manage purchase orders and deliveries |
| 🛒 **Customer Panel** | Self-service menu browsing, cart, order placement, and order tracking |
| 📊 **Admin Dashboard** | Live KPI cards, recent orders, stock alerts, and revenue overview |
| 🏢 **Multi-Branch Support** | Centralized admin control across all branches |

---

## 🛠️ Tech Stack

```
Language      →  Python 3.11+
GUI Framework →  PyQt6 6.5+
Database      →  Microsoft SQL Server 2022 (Express)
DB Driver     →  pyodbc + ODBC Driver 17 for SQL Server
DB Auth       →  Windows Authentication (Trusted Connection)
Styling       →  Custom QSS Design System — "Obsidian & Ember"
PDF Reports   →  reportlab
Charts        →  matplotlib
```

---

## 📁 Project Structure

```
RestaurantMS/
│
├── main.py                        # App entry point
├── theme.py                       # Global QSS design system (Obsidian & Ember)
├── requirements.txt               # Python dependencies
│
├── database/
│   ├── __init__.py
│   └── connection.py              # MS SQL connection + reusable query functions
│
├── modules/
│   ├── __init__.py
│   ├── login.py                   # Login screen (all roles)
│   ├── admin_dashboard.py         # Admin / Manager dashboard
│   ├── orders.py                  # Order management (Waiter)
│   ├── kitchen.py                 # Kitchen Display System (Chef)
│   ├── billing.py                 # Billing & invoices
│   ├── inventory.py               # Inventory tracking
│   ├── menu.py                    # Menu management
│   ├── staff.py                   # Staff management
│   ├── tables.py                  # Table management
│   ├── customer.py                # Customer self-service panel
│   └── supplier.py                # Supplier portal
│
└── sql/
    └── schema.sql                 # Full database schema (run once in SSMS)
```

---

## ✅ Prerequisites

Make sure the following are installed before running the app:

- **Python 3.11+** — [python.org](https://www.python.org/downloads/)
- **Microsoft SQL Server 2022 Express** — [Download](https://www.microsoft.com/en-us/sql-server/sql-server-downloads)
- **SQL Server Management Studio (SSMS)** — [Download](https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms)
- **ODBC Driver 17 for SQL Server** — [Download](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-github-username/restaurant-management-system.git
cd restaurant-management-system
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up the Database

1. Open **SQL Server Management Studio (SSMS)**
2. Connect using **Windows Authentication**
3. Click **New Query**, paste the contents of `sql/schema.sql`, and click **Execute**
4. This creates the `RestaurantDB` database with all tables and sample data

### 5. Configure the Connection

Open `database/connection.py` and update your server name:

```python
DB_CONFIG = {
    "server": r"YOUR-PC-NAME\SQLEXPRESS",   # ← paste your server name from SSMS
    "database": "RestaurantDB",
}
```

> 💡 **How to find your server name:** Open SSMS → the name at the top of the connection dialog is your server name. Copy it exactly.

---

## ▶️ Running the App

```bash
python main.py
```

You should see this in the terminal on successful launch:

```
====================================================
   Restaurant Management System  —  v1.0
====================================================
[startup] Initializing application...
[startup] Connecting to MS SQL Server... ✓  Connected successfully!
[startup] Launching UI...
====================================================
```

---

## 👤 User Roles & Credentials

| Role | Username | Password | Access |
|------|----------|----------|--------|
| **Admin** | `admin` | `admin123` | Full system access, all branches |
| **Manager** | `manager` | `manager123` | Branch operations, staff, inventory |
| **Chef** | `chef` | `chef123` | Kitchen display, order status updates |
| **Waiter** | `waiter` | `waiter123` | Order taking, table management, billing |
| **Customer** | `customer` | `customer123` | Menu browsing, order placement, tracking |
| **Supplier** | `supplier` | `supplier123` | Purchase orders, delivery confirmation |

> ⚠️ These are default development credentials. Change them before any production use.

---

## 🗄️ Database Schema

The system uses **15 tables** in MS SQL Server:

```
branches          → Restaurant branch records
staff             → All users (all roles stored here)
customers         → Customer profiles
categories        → Menu categories
menu_items        → Food and beverage items
restaurant_tables → Physical tables with status
reservations      → Table reservation records
orders            → All order headers
order_details     → Line items per order
suppliers         → Supplier records
inventory         → Raw material stock per branch
purchases         → Purchase orders from suppliers
payments          → Payment records
invoices          → Generated invoices with GST
attendance        → Staff check-in / check-out
```

---

## 📸 Screenshots

> Add screenshots of your app here after running it.

```
screenshots/
├── login.png
├── dashboard.png
├── orders.png
├── kitchen.png
├── billing.png
└── inventory.png
```

To add a screenshot to the README:
```markdown
![Dashboard](screenshots/dashboard.png)
```

---

## 🤝 Contributing

This is a university group project. To contribute:

1. Fork the repository
2. Create your feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes
   ```bash
   git commit -m "Add: your feature description"
   ```
4. Push to the branch
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a **Pull Request**

---

## 📄 License

This project is for academic purposes — **BS Artificial Intelligence, Bahria University Karachi**.

---

<div align="center">

Made with ❤️ by **Group 6** — BS-AI, Bahria University Karachi

</div>
