from pydantic_settings import BaseSettings, SettingsConfigDict

class BotSettings(BaseSettings):
    token: str
    name: str

    @property
    def link(self):
        return f"https://t.me/{self.name}"
    
    model_config = SettingsConfigDict(env_prefix='bot_', env_file='.env', extra='allow')
