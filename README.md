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
- `api/` — application: models, serializers, views, admin, permissions
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

Note: URL paths live in `api/urls.py` and `laundry_api/urls.py` — check those to see exact route names.

Getting started (local)

1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies (uses `pipenv` if you prefer the Pipfile)

```bash
# With pipenv
pip install pipenv
pipenv install

# Or pip (if you have a requirements file)
pip install -r requirements.txt
```

3. Apply migrations and create a superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

4. Run the development server

```bash
python manage.py runserver
```

5. Open the admin at `http://127.0.0.1:8000/admin/` and sign in with the superuser.

Admin notes
- The project uses a custom `User` model that authenticates via `email` (no `username`). The admin forms are wired to use email/password fields when creating users.

Environment variables (common)
- `SECRET_KEY` — Django secret key
- `DEBUG` — `True`/`False`
- `ALLOWED_HOSTS` — hostnames
- `DEFAULT_FROM_EMAIL` — email used when sending notifications

Testing

```bash
python manage.py test
```

Contributing

- Open a PR with tests for any non-trivial change.

License

- MIT (or project-specific) — add a license file if needed.
