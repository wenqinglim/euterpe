# Euterpe: Musical Complexity Analysis API

Euterpe is a Python API for analyzing musical complexity, focusing on components such as harmonic complexity. Built with FastAPI, it leverages music21 for music analysis.

## Features
- Harmonic complexity analysis endpoint (expandable for rhythm, melody, etc.)
- FastAPI for modern, async web APIs
- music21 integration for music parsing and analysis
- Strict code quality: Black, isort, Ruff, mypy, pytest
- Environment/config management with pydantic-settings

## Requirements
- Python 3.11+
- [pyenv](https://github.com/pyenv/pyenv) (for Python version management)
- [uv](https://github.com/astral-sh/uv) (for dependency management)

## Basic Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd euterpe
   ```

2. **Run the setup script:**
   This will install Python, create a virtualenv, install dependencies, and set up pre-commit hooks.
   ```bash
   bash setup.sh
   ```

3. **Activate the environment:**
   ```bash
   pyenv activate euterpe_env
   ```

4. **Run the API server:**
   ```bash
   uv run app/main.py
   # or, using uvicorn directly:
   uv run uvicorn app.main:app --reload
   ```

## Development Setup

- **Install dev dependencies:**
  (Already handled by setup.sh, but you can re-sync anytime)
  ```bash
  uv sync --dev
  ```

- **Code formatting & linting:**
  ```bash
  uv run black app tests
  uv run isort app tests
  uv run ruff check app tests
  uv run mypy app
  ```

- **Run tests:**
  ```bash
  uv run pytest
  ```

- **Pre-commit hooks:**
  Pre-commit hooks are installed by setup.sh. To run them manually:
  ```bash
  uv run pre-commit run --all-files
  ```

## Environment Variables
- Copy `.env.example` to `.env` and set required variables as needed.
- Configuration is managed via `app/config.py` using pydantic-settings.

## Project Structure
```
euterpe/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   └── endpoints/
│   │       └── harmony.py
│   ├── core/
│   │   └── harmony.py
│   ├── services/
│   │   └── music21_service.py
│   └── ...
├── tests/
├── pyproject.toml
├── setup.sh
├── README.md
└── ...
```

## License
MIT

## Etymology
Euterpe (pronounced "yoo-TER-pee") is one of the nine Muses in Greek mythology, specifically the Muse of music and lyric poetry. Her name means "the Giver of Delight" in Ancient Greek (Εὐτέρπη), reflecting the project's aim to bring insight and delight through the analysis of musical complexity.

Euterpe is often depicted playing the aulos, a double-piped wind instrument, symbolizing inspiration and the joy of music—an apt namesake for a tool dedicated to understanding the intricacies of musical art.
