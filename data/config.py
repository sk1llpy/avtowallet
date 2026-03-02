import pytz
import datetime

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

class PostgresSettings(BaseSettings):
    name: str
    user: str
    password: str
    host: str
    port: int
    
    @property
    def url(self) -> str:
        return f"{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    @property
    def async_connector(self) -> str:
        return f"postgresql+asyncpg://{self.url}"

    @property
    def sync_connector(self) -> str:
        return f"postgresql://{self.url}"

    model_config = SettingsConfigDict(env_prefix='db_', env_file='.env', extra='allow')


class DjangoSettings(BaseSettings):
    secret_key: str
    debug: bool
    allowed_hosts: str
    csrf_trusted_origins: str
    domain: str
    
    @property
    def csrf_trusted_origins_list(self) -> list:
        return [origin.strip() for origin in self.csrf_trusted_origins.split(",") if origin.strip()]
    
    @property
    def allowed_hosts_list(self) -> list:
        return [allowed_host.strip() for allowed_host in self.allowed_hosts.split(",") if allowed_host.strip()]

    model_config = SettingsConfigDict(env_prefix='django_', env_file='.env', extra='allow')

class BotSettings(BaseSettings):
    token: str
    name: str

    model_config = SettingsConfigDict(env_prefix='bot_', env_file='.env', extra='allow')

tashkent_tz = pytz.timezone('Asia/Tashkent')
utc = pytz.utc

def current_time(time_zone: bool = False):
    return datetime.datetime.now(tz = (tashkent_tz if time_zone else utc))
