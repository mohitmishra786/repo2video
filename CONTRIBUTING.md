# Contributing to repo2video

Thanks for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/mohitmishra786/repo2video.git
cd repo2video
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install pytest ruff
```

## Running Tests

```bash
pytest tests/ -v
```

## Linting

```bash
ruff check .
```

## Pull Request Process

1. Fork the repository and create a feature branch
2. Add tests for any new functionality
3. Ensure all tests pass: `pytest tests/ -v`
4. Run the linter: `ruff check .`
5. Update documentation if needed
6. Submit a pull request against the `main` branch

## Coding Standards

- Follow PEP 8 with 4-space indentation
- Add type hints to all public functions and methods
- Use descriptive variable names
- Write docstrings for all public modules, classes, and functions

## Issue Tracking

- Use the issue templates for bug reports and feature requests
- Check existing issues before opening a new one
- Include your Python version and OS in bug reports
