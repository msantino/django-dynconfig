# django-dynconfig

[![CI](https://github.com/msantino/django-dynconfig/actions/workflows/ci.yml/badge.svg)](https://github.com/msantino/django-dynconfig/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/django-dynconfig.svg)](https://pypi.org/project/django-dynconfig/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-dynconfig.svg)](https://pypi.org/project/django-dynconfig/)
[![Django versions](https://img.shields.io/badge/django-4.2%20|%205.0%20|%205.1%20|%205.2-blue.svg)](https://pypi.org/project/django-dynconfig/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Dynamic configuration management for Django. Store settings in the database, manage them through the admin, and access them with a simple API. Supports type casting, optional encryption for secrets, and caching.

## Features

- **Simple API** — `get_config("key")` from anywhere in your code
- **Typed values** — Automatic casting to `str`, `int`, `float`, `bool`, `list`, or `json`
- **Admin UI** — Manage configs in Django admin with grouping, search, and filtering
- **Optional encryption** — Encrypt sensitive values (API keys, secrets) at rest
- **Caching** — Uses Django's cache framework with automatic invalidation on save/delete
- **Import/Export** — Management commands to move configs between environments

## Quick Start

```bash
pip install django-dynconfig
```

Add to your `INSTALLED_APPS` and run migrations:

```python
# settings.py
INSTALLED_APPS = [
    ...
    "dynconfig",
]
```

```bash
python manage.py migrate
```

That's it. Open the Django admin and start adding configurations, or use the API:

```python
from dynconfig import get_config, set_config

# Set a config (creates it if it doesn't exist)
set_config("notifications.enabled", True)
set_config("billing.max_retries", 5)
set_config("billing.api_key", "sk_live_...", is_encrypted=True, group="billing")

# Get a config (typed automatically)
get_config("notifications.enabled")      # → True (bool)
get_config("billing.max_retries")        # → 5 (int)
get_config("billing.api_key")            # → "sk_live_..." (decrypted)
get_config("missing.key", default=10)    # → 10
```

## Usage

### Type Casting

Values are stored as strings in the database and cast to Python types on retrieval based on the `value_type` field:

| value_type | Python type | Example stored | Example returned |
|------------|-------------|----------------|------------------|
| `string`   | `str`       | `"hello"`      | `"hello"`        |
| `integer`  | `int`       | `"42"`         | `42`             |
| `float`    | `float`     | `"3.14"`       | `3.14`           |
| `boolean`  | `bool`      | `"true"`       | `True`           |
| `json`     | `dict/list` | `'{"a": 1}'`   | `{"a": 1}`       |
| `list`     | `list`      | `"a, b, c"`    | `["a", "b", "c"]`|

When using `set_config()`, the type is auto-detected from the Python value if not specified.

### Groups

Organize configs by group for cleaner admin views:

```python
set_config("asaas.api_key", "...", group="billing")
set_config("asaas.webhook_secret", "...", group="billing")

# Get all configs in a group
from dynconfig import get_configs_by_group
billing = get_configs_by_group("billing")
# → {"asaas.api_key": "...", "asaas.webhook_secret": "..."}
```

### Encryption

For sensitive values like API keys and secrets:

```bash
pip install django-dynconfig[encryption]
```

```python
# settings.py
DYNCONFIG_ENCRYPTION_KEY = env("DYNCONFIG_ENCRYPTION_KEY")
```

Generate a key:

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

Encrypted values are stored as ciphertext in the database and decrypted transparently on read. The admin shows `••••••••` instead of the raw value.

### Management Commands

```bash
# Export all configs to JSON
python manage.py exportconfigs -o configs.json

# Export only a specific group, excluding secrets
python manage.py exportconfigs -g billing --no-secrets -o billing.json

# Import configs (skip existing by default)
python manage.py importconfigs configs.json

# Import and overwrite existing
python manage.py importconfigs configs.json --overwrite

# Preview without changes
python manage.py importconfigs configs.json --dry-run
```

## Settings

All settings are optional with sensible defaults:

| Setting | Default | Description |
|---------|---------|-------------|
| `DYNCONFIG_CACHE_BACKEND` | `"default"` | Django cache backend to use |
| `DYNCONFIG_CACHE_TIMEOUT` | `300` | Cache TTL in seconds |
| `DYNCONFIG_CACHE_PREFIX` | `"dynconfig"` | Cache key prefix |
| `DYNCONFIG_ENCRYPTION_KEY` | `None` | Fernet key for encryption |
| `DYNCONFIG_RAISE_NOT_FOUND` | `False` | Raise `ConfigNotFoundError` instead of returning `None` |

## Django System Checks

Run `python manage.py check` to verify your configuration. dynconfig will warn you if encrypted config entries exist but `DYNCONFIG_ENCRYPTION_KEY` is not set.

## License

MIT — see [LICENSE](LICENSE).
