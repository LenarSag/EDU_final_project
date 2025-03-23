from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # for jwt creation
    USER_JWT_SECRET_KEY: str = (
        'b0a3f260fecdc69160d4045c276c28fe99bb78a29bf140075b4766b6931b20b0'
    )
    # for jwt creation
    SERVICE_JWT_SECRET_KEY: str = (
        '06d4b337d1845d7c4c9acedf9f14a1762c0b72fb019cc0110311ca23a53a52b7'
    )
    # access between services
    SERVICES_COMMON_SECRET_KEY: str = '5sfTNhq3jjnelsaU3ZG7sj3QV7P0gKyt'

    ALGORITHM: str = 'HS256'

    USER_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30
    SERVICE_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 180

    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_DB: str = 'db'
    DB_HOST: str = 'db'
    DB_PORT: int = 5432

    REDIS_HOST: str = 'redis_service'
    REDIS_PORT: int = 6379

    API_URL: str = '/api/v1'

    @property
    def db_url(self):
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}'

    @property
    def redis_url(self):
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}'


settings = Settings()
