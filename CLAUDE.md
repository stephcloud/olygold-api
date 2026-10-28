# Project Context

## Project
- Name: olygold-api
- Purpose: Backend for an inventory, sales and receipt system for Olygold Venture, a Nigerian wholesaler of poultry farm supplies (feeds, vaccines for chickens and pigs, feeders, drinkers, day-old chicks). One business today, built so more businesses can be added later.
- Working app name: OlyStock (keep it as a single config value, easy to change)
- Frontend repo: olygold-web (Next.js, Tailwind, shadcn on Vercel). Built after the backend. It consumes this API's OpenAPI schema.
- Deployed on: Render, Frankfurt region (auto-deploys from `main`)
- Users are on Android Chrome, later a laptop. Design the API for a mobile-first PWA that may queue sales offline.

Real engineering work. Her stock numbers and customer debts must be right. Correctness beats speed and beats extra features.

## Hard rules (never break these)
1. **Stock is a ledger.** Never store or overwrite a "current stock" number. Every change is a row in `stock_movements` with a signed quantity (opening, purchase, sale, return, adjustment). Current stock = sum of movements.
2. **Stock lives in the smallest base unit.** Feed in kg, vaccines in doses, equipment in pieces. Every way of selling (a bag, a half bag, a kg) is a `sell_option` with a quantity in base units and its own price.
3. **Money is an integer in naira** (BigInteger column). Never floats, never text like "22,200". Commas are a UI concern only.
4. **Quantities are `Numeric(12,3)`, never float.** A half bag of 25kg feed is 12.5. Round money once per line item, in one shared helper.
5. **Every table has `business_id`.** Every query filters by it, through one shared dependency so no route can forget it.
6. **Prices are copied at sale time.** `sale_items` stores the unit price and unit cost used at that moment. Changing a price later never changes past sales or profit.
7. **Never delete sales or payments.** Corrections are new rows (returns, adjustments, reversals).
8. **Customer balances are calculated, never typed.** Balance = sum of credit sales minus sum of payments (and returns).
9. **Cost price and profit are owner-only.** Staff users must never receive them in any response. Use separate response schemas for owner and staff, not a hidden UI field.
10. **Offline-friendly writes.** Sales, payments and stock movements accept a client-generated UUID and `created_at`. Endpoints are idempotent: the same UUID sent twice is saved once and returns the saved record.

## Data model
- `businesses` (name, address, phone_numbers, receipt_footer_text; owner-editable, never hardcoded)
- `users` (business_id, role: owner or staff)
- `products` (category, name, base_unit, low_stock_level)
- `sell_options` (product_id, label, quantity_in_base_units, selling_price, cost_price)
- `stock_movements` (product_id, type, signed quantity, reference to sale or purchase, created_at)
- `batches` (optional, for vaccines: expiry_date, quantity)
- `customers` (name, phone)
- `sales` (customer_id nullable, total, amount_paid, payment_status: paid, part, unpaid, payment_method: cash or transfer, created_by, client_uuid)
- `sale_items` (sale_id, sell_option_id, quantity, unit_price, unit_cost)
- `payments` (customer_id, sale_id nullable, amount, method: cash or transfer, created_at, client_uuid)
- `suppliers`, `purchases`, `purchase_items`

## Credit sales (in scope)
Most sales are cash or transfer, but she can sell on credit and customers pay off debts in pieces.
- A sale takes `amount_paid`. If less than the total, it is a credit sale and `customer_id` is required.
- Walk-in cash sales do not require a customer.
- Payments can be recorded later against a customer, optionally linked to a sale.
- Customer search by name or phone; warn on a duplicate phone number.
- Returns on a credit sale reduce what the customer owes.
- Needed endpoints: customer statement (taken, paid, balance), record payment, debtors list sorted by amount owed.
- Not in scope: interest, credit limits, automatic reminders.

## Receipts
The API returns everything a receipt needs in one call: business name, address, phone numbers, footer text, date, items (label, quantity, unit price, line total), total, amount paid, balance remaining, payment method. The frontend renders it (screen, WhatsApp share, print, later Bluetooth).

## Endpoints (planned, versioned under `/api/v1`)
auth, businesses (settings), products, sell-options, stock (opening, adjustments, current levels), sales, customers, payments, suppliers, purchases, reports (daily sales, profit, low stock, debtors). Spreadsheet import runs as a script or an owner-only endpoint.

## Build phases (each must work on its own; commit after each)
1. Scaffold, schema with `business_id`, auth (owner and staff)
2. Import products and sell options from the spreadsheet (columns: Category, Item_Name, Sell_by_Unit_or_Fraction, SubItem_Name, Selling_Price_SubItem, Cost_Price_SubItem, Stock_Count_SubItem). Clean mixed prices like "22,200" into integers.
3. Opening stock entry
4. Sales: deduct stock through the ledger, receipt payload
5. Customers, credit, payments, debtors list
6. Stock-in (purchases from suppliers)
7. Reports: daily sales, profit, low stock
8. Deploy to Render
9. If time remains: idempotent sync endpoints hardening, expiry alerts

## Out of scope for now
Staff attendance, loyalty, barcode scanning, multi-store, taxes and discounts, signup flow, billing, admin dashboard for other businesses, Redis.

## Environment variables (names only, never values)
`DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `CORS_ORIGINS`, `COOKIE_DOMAIN`, `PORT`

## Deployment
- Backend on Render (paid small web service and small Postgres, Frankfurt); start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Frontend on Vercel; add its production URL to `CORS_ORIGINS`
- API at `api.<domain>`, web at `app.<domain>`. Same parent domain so login cookies work. Set `COOKIE_DOMAIN` accordingly.
- Nightly database backups must be enabled before real data goes in.

---

## Stack
Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, PostgreSQL, pytest. No Redis.

## Folder structure
```
app/
├── main.py            # app creation, middleware, router includes
├── core/              # config.py (settings), security.py
├── db/                # session.py, base.py
├── models/            # SQLAlchemy models
├── schemas/           # Pydantic schemas
├── api/v1/            # routers (thin: validate, call service, return)
├── services/          # business logic
└── tests/             # mirrors app/ structure
alembic/               # migrations
scripts/               # one-off scripts, e.g. import_products.py
```

## Naming conventions
- Python files, functions, variables: `snake_case`. Classes and Pydantic schemas: `PascalCase` (`SaleCreate`, `SaleResponse`).
- Constants and env vars: `UPPER_SNAKE_CASE`.
- Routes: plural nouns, kebab-case, versioned: `/api/v1/sell-options`.
- DB tables: plural snake_case (`sales`). Columns: singular snake_case (`created_at`).
- Migrations: descriptive, e.g. `add_batches_to_products`.
- Branches: `feature/...`, `fix/...`, `chore/...`. Commits: Conventional Commits (`feat:`, `fix:`, `docs:`).

## Code rules
- Routers stay thin; business logic goes in `services/`.
- Type hints everywhere. Separate Pydantic schemas for create, update, and response.
- Never return password hashes or secrets in responses. Hash passwords with argon2.
- Use dependency injection (`Depends`) for DB sessions, auth, and the current business.
- Config only through `core/config.py` (pydantic-settings); never read `os.environ` elsewhere.
- Every endpoint gets at least a success test and a failure test.
- Always paginate list endpoints.
- Tests are mandatory for: stock ledger math, credit balance math, price cleaning in the spreadsheet import, idempotent sale creation, and staff never seeing cost price.
- A sale is saved in one database transaction (sale, sale_items, stock_movements, payment). Either all of it saves or none.
- Files and images go to object storage if ever needed. Store only the URL or key in Postgres.

## Rules for Claude
- Never read or edit `.env`. Update `.env.example` when adding a variable.
- Migrations: until the first Render deploy, the schema is still changing, so you may delete and regenerate the initial migration (ask first, local database only). After the first deploy, never edit a committed migration; create a new one.
- Never run destructive DB commands (drop, truncate, downgrade base) against anything but the local dev database, and ask first.
- Run `/test` before declaring a task done.
- Use the `code-reviewer` subagent after significant changes and `db-reviewer` after model or migration changes.
- Pre-approved dependencies (no need to ask): `fastapi`, `uvicorn`, `sqlalchemy`, `asyncpg`, `alembic`, `pydantic-settings`, `pyjwt`, `argon2-cffi`, `openpyxl`, `httpx`, `pytest`, `pytest-asyncio`, `ruff`. Ask before adding anything else.
- Ask before adding any feature not listed in this file.
- Keep commits small, one working step each.
