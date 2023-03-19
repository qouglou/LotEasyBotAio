from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    db_host: SecretStr
    db_name: SecretStr
    db_user: SecretStr
    db_user_pass: SecretStr
    db_port: SecretStr

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


env_config = Settings()