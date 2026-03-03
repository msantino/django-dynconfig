# Contributing

Thanks for your interest in contributing to django-dynconfig!

## Development Setup

```bash
git clone https://github.com/msantino/django-dynconfig.git
cd django-dynconfig
python -m venv .venv
source .venv/bin/activate
make install
```

## Running Tests

```bash
make test          # Run with coverage
make lint          # Check code style
make format        # Auto-format
```

## Submitting Changes

1. Fork the repo and create a branch from `main`
2. Add tests for any new functionality
3. Ensure all tests pass and linting is clean
4. Submit a pull request

## Code Style

This project uses [ruff](https://github.com/astral-sh/ruff) for linting and formatting. Run `make format` before committing.

## Reporting Issues

Open an issue on [GitHub](https://github.com/msantino/django-dynconfig/issues) with:

- Python and Django versions
- Steps to reproduce
- Expected vs actual behavior
