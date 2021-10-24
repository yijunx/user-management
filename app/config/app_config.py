import os
from pydantic import BaseSettings


class Settings(BaseSettings):

    ENV: str
    SERVICE_NAME: str
    SERVICE_VERSION: str
    DOMAIN_NAME: str
    APP_SECRET: str

    DATABASE_URI: str
    CERTS_DIR: str

    DEFAULT_PAGE_SIZE: int = 5
    CORS_ALLOWED_ORIGINS: str
    USER_ADMIN_ROLE_ID: str

    RESOURCE_NAME: str = "users/"
    OTHER_SERVICES_URL: str = "not set up yet"


class ProdConfig(Settings):
    pass


class DevConfig(Settings):
    class Config:
        env_file = "./config/dev.env"


def get_conf():
    if os.getenv("ENV"):
        return ProdConfig()
    else:
        return DevConfig()


conf = get_conf()

if __name__ == "__main__":
    print(conf)
