import os

postgres_url = os.getenv("POSTGRES_URL")
exp_access_token = os.getenv("EXP_ACCESS_TOKEN")
exp_refresh_token = os.getenv("EXP_REFRESH_TOKEN")

ALGORITHM = "HS256"
SECRET_KEY_JWT = os.getenv("SECRET_KEY_JWT")