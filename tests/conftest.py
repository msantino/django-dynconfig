import pytest

from dynconfig.models import ConfigEntry


@pytest.fixture
def config_entry(db):
    """Create a basic string config entry."""
    return ConfigEntry.objects.create(
        key="test.setting",
        value="hello",
        value_type="string",
        group="test",
        help_text_field="A test setting.",
    )


@pytest.fixture
def config_entries(db):
    """Create a set of typed config entries."""
    entries = [
        ConfigEntry(key="app.name", value="MyApp", value_type="string", group="app"),
        ConfigEntry(key="app.debug", value="true", value_type="boolean", group="app"),
        ConfigEntry(key="app.max_retries", value="5", value_type="integer", group="app"),
        ConfigEntry(key="app.rate_limit", value="1.5", value_type="float", group="app"),
        ConfigEntry(key="app.tags", value="web, api, backend", value_type="list", group="app"),
        ConfigEntry(key="app.metadata", value='{"env": "staging"}', value_type="json", group="app"),
    ]
    return ConfigEntry.objects.bulk_create(entries)


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the cache before each test."""
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()
