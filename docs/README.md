# Smart Inventory & Dynamic Pricing Backend

Production-grade Django backend for a small e-commerce store selling niche products (artisanal kitchenware). Handles catalog, orders, inventory, suppliers, dynamic pricing, multi-currency prices, real-time analytics, and distributed caching.

## Data Model
- **Category:** Product classification, name and description.
- **SupplierProfile:** Supplier details (name, contact, location [PostGIS], address).
- **Product:** Linked to category/supplier, tags, description, stock management, dynamic/multi-currency pricing.
- **CustomerProfile:** Linked to Django User, address, phone, order history.
- **Order:** Linked to customer, tracks status, items, total, timestamps.
- **OrderItem:** Tied to order/product, unit price, quantity.

## Core Features
- **Product Catalog Management:** CRUD for products/categories/tags/suppliers.
- **Order API:** Create/update/cancel orders; transactional stock adjustment.
- **Inventory Alerts & Supplier Restock:** Redis-based caching & low stock alerting, restock endpoint (via services).
- **Currency Rates Integration:** Fetch live rates from API, cache in Redis, auto-update multi-currency prices.
- **Customer & Supplier Profiles:** Relational data, clean schema, Django user integration, location/geospatial data.

## Advanced Features
- **Dynamic Pricing Engine:** Price adjustment logic (stock/demand), multi-step transaction with rollback on logic failure.
- **Real-Time Stock Analytics:** Complex raw SQL queries using JOINs/window functions for sales/stock reporting, analytics API endpoint.
- **Concurrent Stock Updates:** Order placement with row-level locks, transactional conformance; avoids overselling/race conditions.

## Architecture & Patterns
- **Single Django App ('app')**
- **Layered architecture:** Thin views, fat models/services, business logic in service layer
- **Service Layer:** All complex business logic and integrations handled by services
- **Resource-based API:** DRF ViewSets & routers
- **Caching:** Redis for product listing, currency rates, inventory alerts
- **PostGIS for supplier location**

## Caching & Concurrency
- **Redis Caches:** Product lists, inventory alerts, currency rates
- **Transactional Inventory Updates:** Django ORM, row-level locks
- **Savepoints:** Used for dynamic pricing logic

## Setup & Development
Run migrations & tests:
```
make setup
make test
```

Lints:
```
make lint
```

## How To Use
- API endpoints at `/api/`
- Auth via DRF TokenAuthentication
- Analytics at `/api/analytics/`
- Health check at `/api/health/`

## Extensibility
- User authentication via Django user model
- Easy extension for promotions, discount rules, more currencies

## Final Notes
- Designed as a robust, testable foundation for junior backend engineers
- Transactional logic and strong schema for production reliability
