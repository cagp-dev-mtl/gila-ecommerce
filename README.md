# Gila Commerce

Full-stack product catalog and checkout. A Python and FastAPI API, a React and Vite storefront, and PostgreSQL, orchestrated with Docker Compose.

## Running the project locally

You only need Docker and Docker Compose. No local Python or Node install is required.

1. Clone the repository and enter it.
2. Create the environment file from the template:

   ```bash
   cp .env.example .env
   ```

3. Build and start everything:

   ```bash
   make run
   ```

   Without Make, the equivalent is `docker compose up -d --build`.

4. Open the app:

   - Storefront: http://localhost:8080
   - API docs: http://localhost:8000/api/docs

On first start the API applies database migrations and seeds the catalog automatically, so the storefront has products right away.

To stop and remove the stack:

```bash
make down
```

## What you can do

- Browse the catalog with search, category filter, sorting, and pagination.
- Create, edit, and delete products.
- Import products from a CSV upload and see a per-row report.
- Add products to a cart and check out.

## How the catalog is seeded

On startup the API loads a bundled CSV (`api/app/data/products.csv`) when the products table is empty. It runs through the same validation pipeline as a manual upload and logs a summary to the container logs. Restarting against a populated database does nothing.

The example CSV provided for this project was downloaded on September 15, 2026.

Seeding is controlled by two environment variables:

- `SEED_ON_STARTUP` (default `false`, set to `true` in Docker Compose)
- `SEED_FILE` (defaults to the bundled CSV)

To see the import report in the UI instead, set `SEED_ON_STARTUP=false` in `.env`, start with an empty database, and upload `api/app/data/products.csv` from the Import page.

## API reference

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/health` | Liveness check |
| GET | `/api/products` | Search, filter, sort, and paginate products |
| GET | `/api/products/categories` | Distinct category list |
| POST | `/api/products` | Create a product |
| GET | `/api/products/{id}` | Fetch a product |
| PUT | `/api/products/{id}` | Update a product |
| DELETE | `/api/products/{id}` | Delete a product |
| POST | `/api/products/import` | Import products from a CSV upload |
| POST | `/api/orders` | Checkout, accepts an `Idempotency-Key` header |
| GET | `/api/orders/{id}` | Fetch an order |

`GET /api/products` accepts `search`, `category`, `sort` (`name`, `price`, `newest`), `order` (`asc`, `desc`), `page`, and `page_size`.

## Running the tests

```bash
make tests
```

This runs the suite against a dedicated test database and enforces 100% line coverage. Unit tests cover the validation and checkout pipelines; functional tests exercise the API against PostgreSQL.

Tests run in a separate image built from the `test` stage of the API Dockerfile, so development dependencies never ship in the runtime image. The suite creates the `ecommerce_test` database on first run and refuses to run against any database whose name does not contain `test`.

## Other Make targets

Day-to-day commands beyond `make run`, `make down`, and `make tests`:

| Target | Description |
| --- | --- |
| `make logs` | Follow container logs |
| `make lint` | Run ruff |
| `make shell` | Open a shell in the api container |
| `make apply-migration` | Run `alembic upgrade head` |
| `make create-migration REVISION="message"` | Create a new migration |

## Continuous integration

GitHub Actions runs ruff, the pytest suite with the coverage gate, and the storefront build on every pull request. In an organization repository this workflow would be a required status check, blocking merges when lint, tests, or the build fail.

## Design decisions

### Stack and storage

Both SQL and NoSQL were on the table. Checkout needs atomic stock updates and uniqueness guarantees, and the catalog is naturally relational, so PostgreSQL was the better fit than a document store. Money values use `Numeric` rather than floats to avoid rounding drift, and integrity is enforced in the schema: unique constraints on SKU and idempotency key, and check constraints on price, stock, and quantity.

The API is Python and FastAPI. A typed and async framework with first-class OpenAPI docs keeps the surface small and self-documenting. The storefront is React and Vite, served as static files by nginx. A heavier meta-framework was considered and set aside as unnecessary for this scope.

### Structure

Business rules live in small pipelines built from immutable context objects and single-purpose steps, with controllers, repositories, and services forming the shell around them. This keeps the rules easy to test in isolation and keeps side effects at the edges. The alternative of putting logic directly in route handlers is quicker to write but harder to test and reuse.

### CSV import

Real catalog data is messy, so import treats bad rows as data rather than failures. Each row is normalized and validated on its own: currency symbols are stripped, invalid prices and negative stock are rejected, blank rows are skipped, and duplicate SKUs upsert with last-write-wins. The endpoint returns a structured report so the caller sees exactly what happened per row, instead of failing the whole file on the first bad line. Uploads are capped at 5 MB to keep memory use and transaction time bounded.

### Checkout and concurrency

Checkout is transactional and safe under concurrent load. Stock is read with `SELECT ... FOR UPDATE` ordered by product id to avoid deadlocks from inverted lock order. Requests carry an `Idempotency-Key` backed by a unique constraint, and an integrity violation on insert resolves to the already-persisted order, so a retried request never double-charges or double-decrements stock. The storefront keeps one key per cart and regenerates it only when the cart contents change, so a retry after a network failure replays the same order. SKU uniqueness and the product-to-order relationship are enforced by the database as well: a concurrent duplicate SKU or a delete of a purchased product surfaces as a clean conflict response rather than an error. The payment step is a deliberate stub that returns a fake reference, sitting behind the same service boundary a real provider would.

### Seeding

Seeding reuses the import pipeline rather than a separate loader, so seeded data passes the same validation and produces the same report. It runs only when the catalog is empty, which keeps startup idempotent across restarts.

### Testing

The suite enforces 100% line coverage. The gate is used as a design tool: it surfaced and removed dead code, and it caught checkout integrity handling that only fires under a specific race. Coverage scope is controlled through configuration rather than inline directives, keeping source files clean.

### Trade-offs and next steps

- The storefront has no automated tests yet; its build runs in CI. Component and end-to-end tests are the natural next addition.
- Authentication and authorization are out of scope for this iteration.
- For production, the services would ship metrics, traces, and logs to Datadog, with distributed tracing across storefront, API, and database. Monitors would route alerts to Slack for elevated 5xx rates, checkout error spikes, latency, and database saturation.

## Project layout

```
api/         FastAPI application, migrations, tests
storefront/  React and Vite storefront
docker-compose.yml
Makefile
```
