# 🚀 Enterprise E-Commerce GraphQL Backend System

An enterprise-grade, modular e-commerce backend architecture built with **Django**, **Strawberry GraphQL**, and **PostgreSQL**, optimized for high-throughput operations, asynchronous background processing, and global cryptocurrency payments.

---

## 🌟 Key Features

* **Modular Domain-Driven Architecture:** Cleanly partitioned into 9 independent functional apps (Accountant, Catalog, Customers, E-Commerce, Inventory, Marketing, Orders, Payments, Shipping, and Vendors) ensuring high maintainability and loose coupling.
* **Modern GraphQL API:** Powered by **Strawberry GraphQL** with strict JWT authentication, custom permissions, and optimized query resolvers.
* **Crypto Payment Gateway:** Integrated multi-cryptocurrency checkout supporting over 300+ digital assets for seamless, borderless transactions.
* **Asynchronous Task Queue:** High-performance background worker pipeline powered by **Celery** and **Redis** for handling notifications, order processing, and scheduled tasks.
* **Advanced Admin Dashboard:** Customized with the modern **Unfold Admin** theme for professional backend management and role-based access control (RBAC).
* **Robust Testing Suite:** Comprehensive automated testing framework implemented with `pytest-django` and `Faker`.

---

## 🏗️ Project Structure

The project is structured into modular enterprise boundaries:
```text
ecommerce-graphql-api/
├── accountante/       # Financial tracking & accounts management
├── catalog/           # Product categories, items, and attributes
├── customers/         # User profiles and segmentation
├── ecommerce/         # Core project settings, schema, and routing
├── inventory/         # Stock levels and warehouse logistics
├── marketing/         # Campaigns, discounts, and promotions
├── orders/            # Cart, order lifecycle, and fulfillment
├── payments/          # Crypto payment gateway (300+ assets) & transactions
├── shipping/          # Delivery methods and tracking
├── vendors/           # Multi-vendor management and permissions
└── manage.py          # Django project management utility
🛠️ Technology Stack

    Core Framework: Python, Django

    API Layer: Strawberry GraphQL, Strawberry JWT

    Database: PostgreSQL

    Caching & Queue: Redis, Celery

    Payments: NOWPayments / Crypto Gateway Integration

    Testing: Pytest, Pytest-Django
