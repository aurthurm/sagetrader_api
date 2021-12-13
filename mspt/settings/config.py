import os

def getenv_boolean(var_name, default_value=False):
    result = default_value
    env_value = os.getenv(var_name)
    if env_value is not None:
        result = env_value.upper() in ("TRUE", "1")
    return result

def getenv_value(value, default_value=None):    
    env_value = os.getenv(value)
    if env_value is None:
        env_value = default_value
    return env_value

API_V1_STR = "/api/v1"

SECRET_KEY = os.getenvb(b"SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = "DURdlxzKW4LsTaDWKioKuiL8oimGY0o0j5Z_ztT-q84"  # secrets.token_urlsafe(32)

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8  # 60 minutes * 24 hours * 8 days = 8 days

SERVER_NAME = os.getenv("SERVER_NAME")
SERVER_HOST = os.getenv("SERVER_HOST")
BACKEND_CORS_ORIGINS = os.getenv(
    "BACKEND_CORS_ORIGINS"
)  # a string of origins separated by commas, e.g: "http://localhost, http://localhost:4200, http://localhost:3000, http://localhost:8080, http://local.dockertoolbox.tiangolo.com"
PROJECT_NAME = os.getenv("PROJECT_NAME")
if not PROJECT_NAME:
	PROJECT_NAME = "FastAPI Starter Essentials"
SENTRY_DSN = os.getenv("SENTRY_DSN")

POSTGRES_SERVER = getenv_value("POSTGRES_SERVER", 'localhost')
POSTGRES_USER = getenv_value("POSTGRES_USER", 'mspt_user')
POSTGRES_PASSWORD = getenv_value("POSTGRES_PASSWORD", 'mspt_access')
POSTGRES_DB = getenv_value("POSTGRES_DB", 'mspt_db')

try:
    DATABASE_URI = os.environ['DATABASE_URL'] # Heroku
except Exception:
    DATABASE_URI = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
    )

SQLALCHEMY_DATABASE_URI = DATABASE_URI
# SQLALCHEMY_DATABASE_URI = "sqlite:///testing.db"

SMTP_TLS = getenv_boolean("SMTP_TLS", True)
SMTP_PORT = None
_SMTP_PORT = os.getenv("SMTP_PORT")
if _SMTP_PORT is not None:
    SMTP_PORT = int(_SMTP_PORT)
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAILS_FROM_EMAIL = os.getenv("EMAILS_FROM_EMAIL")
EMAILS_FROM_NAME = PROJECT_NAME
EMAIL_RESET_TOKEN_EXPIRE_HOURS = 48
EMAIL_TEMPLATES_DIR = "/app/app/email-templates/build"
EMAILS_ENABLED = SMTP_HOST and SMTP_PORT and EMAILS_FROM_EMAIL

FIRST_SUPERUSER = os.getenv("FIRST_SUPERUSER")
if not FIRST_SUPERUSER:
	FIRST_SUPERUSER = "admin"
FIRST_SUPERUSER_PASSWORD = os.getenv("FIRST_SUPERUSER_PASSWORD")
if not FIRST_SUPERUSER_PASSWORD:
	FIRST_SUPERUSER_PASSWORD = "sniper123"
FIRST_SUPERUSER_EMAIL = os.getenv("FIRST_SUPERUSER_EMAIL")
if not FIRST_SUPERUSER_EMAIL:
	FIRST_SUPERUSER_EMAIL = "sniper@mspt.com"

USERS_OPEN_REGISTRATION = getenv_boolean("USERS_OPEN_REGISTRATION")
if not USERS_OPEN_REGISTRATION:
	USERS_OPEN_REGISTRATION = True

EMAIL_TEST_USER = "test@example.com"