# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-03

### Added

- `ConfigEntry` model with key-value storage, type casting, and grouping
- `get_config()`, `set_config()`, `get_configs_by_group()` service API
- Django admin with grouped display, search, filtering, and masked encrypted values
- Optional Fernet encryption for sensitive values (`pip install django-dynconfig[encryption]`)
- Django cache framework integration with automatic signal-based invalidation
- `exportconfigs` and `importconfigs` management commands
- Django system check for missing encryption key (`dynconfig.W001`)
- Support for Python 3.10–3.13 and Django 4.2–5.2
