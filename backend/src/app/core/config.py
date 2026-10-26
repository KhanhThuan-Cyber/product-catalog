from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- Redis & Cache ---
    REDIS_URL: str = "redis://localhost:6379/0"
    # TTL tính bằng giây
    CACHE_TTL_PRODUCT_DETAIL: int = 600   # 10 phút
    CACHE_TTL_PRODUCT_LIST: int = 300     # 5 phút
    CACHE_TTL_CATEGORY: int = 1800        # 30 phút
    # Tiền tố namespace cho cache key (tuỳ chọn, mặc định rỗng)
    CACHE_KEY_PREFIX: str = ""

    # --- Rate limiting (Fixed Window) ---
    RATE_LIMIT_LOGIN_MAX: int = 10        # số request tối đa / cửa sổ
    RATE_LIMIT_LOGIN_WINDOW: int = 900   # cửa sổ 15 phút (giây)
    RATE_LIMIT_REGISTER_MAX: int = 5
    RATE_LIMIT_REGISTER_WINDOW: int = 3600  # 1 giờ (giây)

    # --- Refresh token ---
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
