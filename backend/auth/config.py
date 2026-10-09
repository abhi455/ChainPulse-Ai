from datetime import timedelta

from config.settings import APP_ENV


JWT_ALGORITHM = "HS256"

JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60

JWT_SECRET_KEY = "CHANGE_THIS_CHAINPULSE_SECRET_IN_PRODUCTION"

if APP_ENV == "production" and JWT_SECRET_KEY.startswith("CHANGE_"):
    raise RuntimeError(
        "JWT_SECRET_KEY must be configured in production."
    )

JWT_ACCESS_TOKEN_EXPIRE = timedelta(
    minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
)
