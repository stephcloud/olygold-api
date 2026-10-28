from app.core.config import Settings


def make_settings(**overrides: str) -> Settings:
    values = {"database_url": "postgresql://u:p@host/db", "secret_key": "x"} | overrides
    return Settings(_env_file=None, **values)


def test_render_database_url_uses_asyncpg() -> None:
    assert make_settings().database_url == "postgresql+asyncpg://u:p@host/db"
    assert (
        make_settings(database_url="postgres://u:p@host/db").database_url
        == "postgresql+asyncpg://u:p@host/db"
    )


def test_asyncpg_database_url_is_unchanged() -> None:
    url = "postgresql+asyncpg://u:p@host/db"
    assert make_settings(database_url=url).database_url == url


def test_cors_origins_split_on_commas() -> None:
    settings = make_settings(cors_origins="http://a.test, https://b.test,")
    assert settings.cors_origins == ["http://a.test", "https://b.test"]


def test_empty_cookie_domain_is_none() -> None:
    assert make_settings(cookie_domain="").cookie_domain is None
