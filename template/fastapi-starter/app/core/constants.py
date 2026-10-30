"""Application-wide constants.

Every string or number that would otherwise be repeated ("magic values") lives here,
so it is defined once, easy to find, and safe to change.
"""

# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------
AUTH_PREFIX = "/auth"
ITEMS_PREFIX = "/items"
ADMIN_PREFIX = "/admin"
USERS_PREFIX = "/user"
HEALTH_PATH = "/health"

AUTH_TAG = "auth"
ITEMS_TAG = "items"
ADMIN_TAG = "admin"
USERS_TAG = "user"
HEALTH_TAG = "health"

# Relative URL the OAuth2 "Authorize" button in Swagger UI posts to.
TOKEN_URL = "auth/token"

# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------
ROLE_ADMIN = "admin"
ROLE_USER = "user"

# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------
JWT_ALGORITHM = "HS256"
TOKEN_TYPE_BEARER = "bearer"

CLAIM_SUBJECT = "sub"
CLAIM_USER_ID = "user_id"
CLAIM_ROLE = "role"
CLAIM_EXPIRES = "exp"

# ---------------------------------------------------------------------------
# Column sizes and validation limits
# (shared by models and schemas so database and API limits never drift apart)
# ---------------------------------------------------------------------------
USERNAME_MAX_LENGTH = 100
EMAIL_MAX_LENGTH = 255
NAME_MAX_LENGTH = 100
PASSWORD_HASH_MAX_LENGTH = 255
ROLE_MAX_LENGTH = 50

ITEM_NAME_MIN_LENGTH = 3
ITEM_NAME_MAX_LENGTH = 100
ITEM_DESCRIPTION_MAX_LENGTH = 500

PASSWORD_MIN_LENGTH = 6

# ---------------------------------------------------------------------------
# Response messages
# ---------------------------------------------------------------------------
HEALTHY_STATUS = "healthy"

COULD_NOT_VALIDATE_CREDENTIALS = "Could not validate credentials"
INVALID_CREDENTIALS = "Invalid credentials"
INSUFFICIENT_PERMISSIONS = "Insufficient permissions"
USER_ALREADY_EXISTS = "Username or email already exists"
ITEM_NOT_FOUND = "Item with id {item_id} not found"
INCORRECT_CURRENT_PASSWORD = "Incorrect current password"
PASSWORD_MUST_DIFFER = "New password must differ from current password"

USER_CREATED = "User created successfully"
PASSWORD_CHANGED = "Password changed successfully"
