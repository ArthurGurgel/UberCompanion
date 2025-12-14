# Deploying on Render (quick guide)

When deploying this Flask app to Render, set the following **Environment Variables** in the Render dashboard (Service → Environment):

Required:
- DB_HOST - hostname or IP of your MySQL server
- DB_USER - database username
- DB_PASSWORD - database password
- DB_NAME - database name

Optional:
- DB_PORT - port (default: 3306)
- SECRET_KEY - Flask secret key (recommended)

Notes:
- We intentionally add `.env` to `.gitignore`. In production you should set env vars via Render's dashboard or secrets mechanism.
- For local development you can create a `.env` file and the app will load it using `python-dotenv` if available. Copy `.env.example` to `.env` and fill values.
- If you see an error such as `Missing required environment variable: DB_HOST` during startup, make sure all required variables are set on Render (or locally in a `.env`).

Troubleshooting:
- `TypeError: int() argument must be a string...` - usually means `DB_PORT` was missing; Render needs DB_PORT set or we default to 3306.
- `Invalid DB_PORT value: ...` - ensure `DB_PORT` is a valid number.

Security:
- Avoid committing sensitive credentials to git. Use Render's environment variables or secret management.

If you want, I can add a small healthcheck endpoint that verifies DB connectivity on startup and logs a friendly message in Render logs.