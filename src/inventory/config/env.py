from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Laden Sie die .env-Datei
load_dotenv(dotenv_path=".env")

class Env(BaseSettings):
    PROJECT_NAME: str = "Inventory Service"
    KC_SERVICE_HOST: str
    KC_SERVICE_PORT: str
    KC_SERVICE_REALM: str
    KC_SERVICE_CLIENT_ID: str
    APP_ENV: str
    EXCEL_EXPORT_ENABLED: str
    EXPORT_FORMAT: str
    KAFKA_URI: str
    TEMPO_URI: str
    PRODUCT_GRAPHQL_URL: str
    KEYS_PATH: str

    class Config:
        env_file = ".env"  # Stellen Sie sicher, dass dies auf Ihre .env-Datei verweist
        env_file_encoding = "utf-8"
        case_sensitive = True

env = Env()
