# Laundry Management API

Lightweight Django REST API for managing laundry shops, shop owners and customers.

Tech stack
- Python 3.12
- Django
- Django REST Framework
- SQLite (default `db.sqlite3`) — can be swapped for Postgres/PostGIS if needed

Project layout (important files)
- `manage.py` — Django management
- `Pipfile` — project dependencies
- `api/` — application: modelsexit, serializers, views, admin, permissions
- `laundry_api/` — Django project settings and WSGI/ASGI

Main models
- `User` — custom user model using `email` as the `USERNAME_FIELD` (user types: `customer`, `shop_owner`, `admin`)
- `Shop` — laundry shop linked to a `User` owner (one owner may have multiple shops)
- `Cloth_type` — cloth types and prices linked to a `Shop`

Key features
- Customer registration and login (token-based)
- Admin-managed shop owner creation and shop approval
- Shop listing, filtering, and nearby-shop calculations
- Admin dashboard for shops and users

Important views / endpoints
- Customer registration: `CustomerRegisterView`
- Login: `LoginView`
- Admin create shop owner: `AdminCreateShopOwnerView`
- Shop list / detail: `ShopListView`, `ShopDetailView`
- Nearby shops: `NearbyShopsView`
- Shop owner management (list of their shops): `ShopOwnerShopView`
