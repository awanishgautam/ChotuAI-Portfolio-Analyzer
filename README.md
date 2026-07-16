# ChotuAI Portfolio Analyzer

An AI-assisted portfolio analytics dashboard for Zerodha and ICICI Direct holdings. It provides portfolio valuation, allocation, benchmark comparisons, return statistics, risk metrics, and natural-language portfolio questions through a Streamlit interface.

## Requirements

- Python 3.12 or newer
- Broker API credentials for live holdings
- An OpenAI API key for AI analysis (optional)

## Setup

Create and activate a virtual environment, then install the project and development tools:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Copy `.env.example` to `.env` and fill in credentials locally:

```powershell
Copy-Item .env.example .env
```

`.env` is intentionally ignored by Git. Never commit API keys, secrets, access tokens, or exported account data.

## Run the dashboard

```powershell
streamlit run app.py
```

Select the broker in the sidebar and use its login flow. Credentials are loaded from the project-local `.env` file, so they do not need to be entered repeatedly in the UI.

## Validation

Run the deterministic test suite with coverage:

```powershell
python -m pytest -q --cov --cov-report=term-missing
```

The tests do not contact broker APIs or require live credentials.

## Project layout

- `app.py` — Streamlit application entry point
- `portfolio/` — portfolio domain models, builders, and calculations
- `analytics/` — returns, benchmark, and risk analytics
- `providers/` — broker and market-data integrations
- `services/auth/` — broker authentication flows
- `app_config/` — `.env`-backed application settings
- `tests/` — deterministic unit tests

## Security

Keep `.env` private and rotate any credential that may have been exposed. Runtime logs, virtual environments, caches, and coverage output are excluded by `.gitignore`.
