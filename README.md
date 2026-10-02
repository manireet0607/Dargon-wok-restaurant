# Dragon Wok

A Chinese restaurant web app with a clear three-tier design. Customers browse the menu, fill a cart, place Cash on Delivery orders and see their order history. Staff use an admin dashboard to manage food, categories, customers and orders.

## 1. Architecture

```
 Browser                    Application tier                 Data tier
┌───────────────┐  HTTPS   ┌─────────────────────┐   TLS    ┌──────────────────┐
│ React (Vite)  │ ───────► │ FastAPI  /api/v1    │ ───────► │ MySQL 8          │
│ S3+CloudFront │   JSON   │ ECS / EC2 (Docker)  │ private  │ Amazon RDS       │
│ or nginx      │ ◄─────── │ JWT, roles, rules   │  subnet  │ (private subnet) │
└───────────────┘          └─────────────────────┘          └──────────────────┘
```

- The browser never talks to the database. Only the backend knows the database password and the JWT secret.
- The backend calculates every price and total itself. The browser only sends item ids and quantities.

## 2. Technology

| Tier | Tools |
|---|---|
| Presentation | React 18, React Router, Vite, plain CSS |
| Application | Python 3.12, FastAPI, SQLAlchemy 2, Pydantic 2, Alembic, PyJWT, bcrypt |
| Data | MySQL 8 (local container or Amazon RDS MySQL) |
| Tools | Docker, Docker Compose, pytest |

## 3. Folder structure

```
dragon-wok/
├── frontend/                React app (src/components, pages, services, context, hooks)
│   ├── src/pages/admin/     Admin dashboard pages
│   ├── Dockerfile, nginx.conf
├── backend/
│   ├── app/
│   │   ├── api/v1/          Routes: auth, users, public (menu), orders, admin
│   │   ├── core/            Settings, security (JWT, bcrypt), logging
│   │   ├── models/          SQLAlchemy tables
│   │   ├── schemas/         Pydantic request/response models
│   │   ├── services/        Order rules, totals, payment providers
│   │   ├── db/              Engine/session, seed script
│   │   └── main.py          App, CORS, health checks
│   ├── alembic/             Migrations
│   ├── tests/               pytest tests (33)
│   └── Dockerfile, entrypoint.sh
├── database/init.sql        Optional: schema + sample data as plain SQL
├── docker-compose.yml
├── .env.example
└── README.md
```

## 4. Prerequisites

- Docker and Docker Compose (easiest), **or** Python 3.12+, Node.js 20+ and a MySQL 8 server.

## 5. Quick start with Docker Compose

```bash
cp .env.example .env
# Edit .env: set SECRET_KEY, MYSQL_ROOT_PASSWORD, DB_PASSWORD, SEED_ADMIN_PASSWORD
docker compose up --build
```

| What | URL |
|---|---|
| Website | http://localhost:3000 |
| API | http://localhost:8000 (docs at /docs in development) |
| Admin login | http://localhost:3000/admin/login |

The backend container waits for MySQL, runs the migrations, adds the sample menu and creates the admin user (email and password from `SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD`). The MySQL data lives in the `mysql_data` volume. Port 3306 is published on `127.0.0.1` only. The database is on a private Docker network shared only with the backend.

Stop with `docker compose down`. Add `-v` to also delete the database volume.

## 6. Local install without Docker

**Database:** create a MySQL database and user:

```sql
CREATE DATABASE dragonwok CHARACTER SET utf8mb4;
CREATE USER 'dragonwok'@'localhost' IDENTIFIED BY 'your-password';
GRANT ALL ON dragonwok.* TO 'dragonwok'@'localhost';
```

**Backend:**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                                  # fill in the values
alembic upgrade head                                  # create tables
python -m app.db.seed                                 # sample menu + admin user
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
cp .env.example .env          # VITE_API_URL=http://localhost:8000/api/v1
npm install
npm run dev                   # http://localhost:5173
```

## 7. Environment variables

See `.env.example` for the full list with comments. The important ones:

| Variable | Meaning |
|---|---|
| `ENVIRONMENT` | `development` or `production`. Production refuses to start with a weak `SECRET_KEY`, `*` in CORS, or database TLS switched off. It also hides `/docs`. |
| `SECRET_KEY` | Signs JWT tokens. Use 32+ random characters. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token life (default 60). |
| `CORS_ORIGINS` | Comma separated list of allowed website origins. |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Database connection. Or set one `DATABASE_URL`. |
| `DB_SSL_ENABLED`, `DB_SSL_CA`, `DB_SSL_VERIFY_IDENTITY` | TLS with certificate and host name checks (for RDS). |
| `DELIVERY_FEE`, `TAX_RATE`, `FREE_DELIVERY_ABOVE` | Fees, all in INR. `TAX_RATE=0.05` means 5%. |
| `SEED_ADMIN_EMAIL`, `SEED_ADMIN_PASSWORD` | Admin created by the seed script. No password means no admin is created. |
| `RUN_MIGRATIONS`, `RUN_SEED` | Container start-up steps. |
| `VITE_API_URL` | Public API address, baked into the frontend at build time. |

## 8. Database, migrations and seed data

- Tables: `users`, `categories`, `menu_items`, `orders`, `order_items`. They use primary keys, foreign keys (`RESTRICT` for history), unique and lookup indexes and `CHECK` constraints (roles, status values, positive prices and quantities).
- All money columns are `DECIMAL(10,2)`. `order_items.unit_price` stores the price at the time of the order, so old orders never change when the menu changes.
- Two columns were added to `orders` beyond your list: `customer_name` and `customer_phone`, because checkout collects them.
- Migrations: `alembic upgrade head` (create/update), `alembic downgrade -1` (undo one step), `alembic revision --autogenerate -m "message"` (new change after editing models).
- Seed data: `python -m app.db.seed` is safe to run again. It adds the 8 categories, 19 dishes and the admin user, and skips what exists.
- `database/init.sql` has the same schema and sample menu as plain SQL. Use **either** it **or** Alembic on an empty database. It already marks the migration as applied, so Alembic works after it. It does not create the admin user, so run the seed script.

## 9. API

Base path: `/api/v1`. Send `Authorization: Bearer <token>` where marked. Money values are strings such as `"149.00"`.

| Method and path | Who | Purpose |
|---|---|---|
| `POST /auth/register` | Public | Create a customer account. Returns a token. |
| `POST /auth/login` | Public | Log in. Returns a token and user. |
| `GET /users/me` | Customer | Own profile. |
| `GET /config` | Public | Delivery fee and tax rate used for the cart estimate. |
| `GET /categories` | Public | Categories. |
| `GET /menu` | Public | Menu. Filters: `category_id`, `food_type` (`veg`/`non_veg`), `search`. |
| `GET /menu/{id}` | Public | One dish. |
| `POST /orders` | Customer | Place an order (items, name, phone, address, notes). |
| `GET /orders` | Customer | Own order history. |
| `GET /orders/{id}` | Customer | Own order detail. |
| `POST /orders/{id}/cancel` | Customer | Cancel own order, only while pending. |
| `GET /admin/stats` | Admin | Orders, revenue (delivered orders), customers, menu items. |
| `GET/POST /admin/categories`, `PUT/DELETE /admin/categories/{id}` | Admin | Manage categories. |
| `GET/POST /admin/menu`, `PUT/DELETE /admin/menu/{id}` | Admin | Manage food items. |
| `PATCH /admin/menu/{id}/availability` | Admin | Turn availability on or off. |
| `GET /admin/orders` (`?status=`), `GET /admin/orders/{id}` | Admin | All orders and details with customer info. |
| `PATCH /admin/orders/{id}/status` | Admin | Change order status. |
| `GET /admin/customers` | Admin | Customer list. |
| `GET /health`, `GET /health/ready` | Public | Liveness, and readiness (checks the database). |

Status flow: `pending → confirmed → preparing → out_for_delivery → delivered`. Cancel is allowed from pending, confirmed and preparing. Skipping steps or changing a finished order returns `409`. Cash on Delivery orders become `paid` when marked delivered.

The cart is kept in the browser (local storage). A server-side cart was optional in your brief and is not included.

Payments are behind `app/services/payment.py`. To add an online gateway, write a new `PaymentProvider`, register it, and allow its name in `OrderCreate.payment_method`.

## 10. Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest -q
```

The 33 tests use an in-memory SQLite database, so no MySQL is needed. They cover registration and login, tokens, roles, menu, order creation and totals, invalid orders, price snapshots, admin menu and category management, and order status rules.

## 11. AWS RDS configuration

1. Create an RDS MySQL 8 instance in **private subnets** (a DB subnet group with no internet route). Set **Publicly accessible = No**. Turn on encryption at rest, automated backups and deletion protection.
2. Create two security groups: `dragonwok-backend-sg` (for the backend) and `dragonwok-db-sg` (for RDS). On `dragonwok-db-sg` allow inbound **TCP 3306 only from `dragonwok-backend-sg`**. Do not allow any CIDR range.
3. Keep the master password in AWS Secrets Manager. Create a separate app user with rights only on the `dragonwok` database. Do not use the master user in the app.
4. Connect with TLS and certificate checks. The backend image already contains the RDS CA bundle:

```
DB_HOST=<your-instance>.<id>.<region>.rds.amazonaws.com
DB_NAME=dragonwok
DB_USER=<app user>
DB_PASSWORD=<from Secrets Manager>
DB_SSL_ENABLED=true
DB_SSL_CA=/certs/rds-global-bundle.pem
DB_SSL_VERIFY_IDENTITY=true
```

   Optional: also require TLS on the server by setting `require_secure_transport=1` in the RDS parameter group.
5. Create the first admin: run one container with `RUN_SEED=true` and `SEED_ADMIN_PASSWORD` set. Then set `RUN_SEED=false`.

## 12. AWS deployment (nothing is created automatically)

Suggested layout:

- **Frontend:** build with `VITE_API_URL=https://api.your-domain.com/api/v1 npm run build`, upload `frontend/dist` to a private S3 bucket and serve it through CloudFront (Origin Access Control). In CloudFront, map the 403 and 404 errors to `/index.html` with status 200 so React Router links work. Alternatively run the frontend Docker image on ECS.
- **Backend:** push `backend/` to Amazon ECR and run it on ECS Fargate (or EC2) behind an Application Load Balancer. Use an ACM certificate so the API is HTTPS.
  - Target group health check: `GET /health`.
  - Task logging: `awslogs` driver to a CloudWatch log group. The app writes JSON lines to stdout.
  - Secrets: put `SECRET_KEY` and `DB_PASSWORD` in Secrets Manager or SSM Parameter Store and inject them as task secrets. Put plain settings in task environment variables.
  - Settings: `ENVIRONMENT=production`, `CORS_ORIGINS=https://your-cloudfront-domain-or-site`, `RUN_SEED=false`.
  - Migrations: with more than one task, set `RUN_MIGRATIONS=false` and run `alembic upgrade head` once as a one-off ECS task using the same image, before each release.
- **Network:** public subnets for the ALB (and CloudFront), private subnets for backend tasks and RDS. Backend security group: allow port 8000 only from the ALB. Give private subnets a NAT gateway if the backend needs outbound internet.
- **Order of work:** VPC and subnets → security groups → RDS → ECR and push image → run migration task → ECS service and ALB → S3 and CloudFront → DNS.

## 13. Security notes

- Passwords: bcrypt (12 rounds). Passwords need 8 to 72 characters with a letter and a number.
- JWT: signed with `SECRET_KEY`, expires after 60 minutes by default. The role is read from the database on each request, so removing admin rights works at once.
- Roles: all `/admin` routes require an admin. Public registration only creates customers.
- Orders: totals, fees and prices come from the server. Client-sent prices and statuses are ignored. Status changes follow a fixed rule table. Customers can only see and cancel their own pending orders (other people's order ids return 404).
- SQL: only SQLAlchemy parameterised queries.
- Errors: unexpected errors return a generic message. Details go to the logs only.
- CORS: only the listed origins. Production refuses `*`.
- Login uses the same error for a wrong email or a wrong password.
- Production mode hides the interactive API docs.

Known limits and what to add before real customers use it:

- The token is stored in the browser's local storage, which a cross-site scripting bug could read. The app does not render raw HTML, which lowers that risk. For stronger protection, move to httpOnly cookies.
- There is no rate limiting or lockout on login. Use AWS WAF rate rules on the ALB or CloudFront.
- There is no email verification or password reset.
- The food pictures in `frontend/public/images` are simple drawn illustrations, not photos. Upload real photos to S3 and set each item's image URL in the admin dashboard.
- The contact details in `src/pages/Contact.jsx` are samples.

## 14. Troubleshooting

| Problem | Fix |
|---|---|
| Backend exits with "SECRET_KEY must be set" | Set a 32+ character `SECRET_KEY`. Required when `ENVIRONMENT=production`. |
| "DB_SSL_ENABLED must be true in production" | Turn on database TLS, or set `ENVIRONMENT=development` for local use. |
| Browser shows a CORS error | Add the website's exact origin (scheme, host, port) to `CORS_ORIGINS` and restart the backend. |
| Frontend shows "Cannot reach the server" | Check `VITE_API_URL`. It is read at build time, so rebuild after changing it. |
| Cannot connect to RDS | Check the backend is in the same VPC, `dragonwok-db-sg` allows `dragonwok-backend-sg` on 3306, and the host name is correct. |
| TLS certificate error to RDS | Check `DB_SSL_CA` points to the bundle file and you use the instance's real host name (not an IP). |
| `Access denied for user` | Check the user, password and that the user has rights on the database. |
| Cannot log in as admin | Run the seed script with `SEED_ADMIN_PASSWORD` set. It never changes an existing admin's password. |
| Refreshing a page gives 404 on S3/CloudFront/nginx | Add the SPA fallback to `/index.html` (already in `nginx.conf`; see section 12 for CloudFront). |
| Port 3306 already in use | Stop the local MySQL, or change the port mapping in `docker-compose.yml`. |
| Delete food item returns 409 | The item is in past orders. Turn off its availability instead. |
