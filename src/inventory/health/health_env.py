from pydantic_settings import BaseSettings, SettingsConfigDict


class HealthSettings(BaseSettings):
    PROMETHEUS_HEALTH_URL: str = "http://localhost:9090/-/healthy"
    TEMPO_HEALTH_URL: str = "http://localhost:3200/metrics"
    MYSQL_HEALTH_ENABLED: str
    KEYCLOAK_HEALTH_URL: str

    model_config = SettingsConfigDict(env_file=".health.env")


health_settings = HealthSettings()
