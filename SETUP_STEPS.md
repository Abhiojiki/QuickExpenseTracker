# ExpenseTracker — Setup & Deploy Guide (local → GitHub → Heroku + S3)

This file contains a concise, reproducible set of steps to set up the project locally, keep secrets out of Git, push to GitHub, and deploy to Heroku using WhiteNoise for static files and AWS S3 for media.

## Quick goals
- Create a reproducible local dev environment
- Keep secrets out of source control (.env + .gitignore)
- Deploy to GitHub + Heroku using WhiteNoise for static files and S3 for user uploads

---

## 1) Prerequisites
- Python 3.10+ (ensure `py`/`python` is on PATH)
- Node.js LTS (for Tailwind/npm tasks)
- Git
- A GitHub account

Recommended package manager: `uv` (lightweight helper that integrates venv and package commands). Traditional option: `pip` (works everywhere).

Install `uv` (Windows PowerShell):
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

If you prefer the traditional tools, skip `uv` and use Python's `venv` + `pip` (examples below).

## 2) Create project folder and virtual environment
PowerShell (from project root). Preferred (uv):
```powershell
cd "C:\Users\Ojas\3D Objects\ResumeProject"
mkdir ExpenseTracker
cd ExpenseTracker

# Create a virtual environment with uv (recommended)
uv venv .venv

# Activate the venv (Windows PowerShell)
.\.venv\Scripts\Activate

# Use uv to add packages into the venv (example)
# uv add <package>
```

Alternative (traditional venv + pip):
```powershell
cd "C:\Users\Ojas\3D Objects\ResumeProject\ExpenseTracker"
py -3 -m venv .venv
.\.venv\Scripts\Activate
python -m pip install --upgrade pip setuptools wheel
```

## 3) Install dependencies (local dev)
Add dependencies to `requirements.txt` (example minimal set):
```text
Django>=4.2
djangorestframework
djangorestframework-simplejwt
django-tailwind
gunicorn
whitenoise
django-storages[boto3]
boto3
psycopg2-binary   # for Postgres in production (optional locally)
```

Install them (preferred with uv, which runs inside the venv):
```powershell
# With uv (adds packages into the active .venv)
uv add -r requirements.txt

# Or, with pip (traditional)
pip install -r requirements.txt
```

## 4) Project config (use environment variables)
- In `mysite/settings.py` replace hard-coded secrets/config with environment variables. Use `python-decouple` or `os.environ`.
- Example patterns (simplified):

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-for-local')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# WhiteNoise for static files in production
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... rest of middleware
]

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# To use S3 for media in production configure DEFAULT_FILE_STORAGE via env vars
```

Notes:
- Keep `DEBUG=True` only on local dev. In production set `DJANGO_DEBUG=False`.
- Add `whitenoise` and configure `STATIC_ROOT` for collectstatic.

## 5) Tailwind (if using) and templates
- Initialize tailwind app if using Django-tailwind (optional):
```powershell
py manage.py tailwind init theme
py manage.py tailwind install
py manage.py tailwind start  # dev only
```

Make sure your templates include `{% load static %}` and that forms include `{% csrf_token %}`.

## 6) Local DB & migrations
```powershell
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
# open http://127.0.0.1:8000
```

## 7) Static files for production (WhiteNoise)
- In `settings.py` ensure:
```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```
- Collect static before production: `py manage.py collectstatic --noinput` (Heroku does this automatically if `collectstatic` is enabled).

## 8) Using AWS S3 for uploaded media (recommended for Heroku)
- Install `django-storages[boto3]` and `boto3`.
- Set these env vars on Heroku (or your platform):
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - AWS_STORAGE_BUCKET_NAME
  - AWS_S3_REGION_NAME (optional)

- Example settings to use S3 for media only:
```python
if os.environ.get('USE_S3') == 'True':
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_QUERYSTRING_AUTH = False
```

Notes: you can keep WhiteNoise for static files and S3 for MEDIA files (uploads).

## 9) Prepare repository (git) and secrets
1. Add files and commit:
```powershell
git init
git add .
git commit -m "Initial commit"
```
2. Create a `.env` locally with secrets (do not commit). Use `.env.example` in repo to show required vars.

## 10) `.gitignore` (do not commit secrets)
- Add a `.gitignore` at repo root. See the `.gitignore` file in this repo for recommended patterns.

## 11) Push to GitHub
```powershell
git remote add origin https://github.com/<your-user>/<repo>.git
git branch -M main
git push -u origin main
```

## 12) Deploy to Heroku (fast demo)
1. Create Heroku app and Postgres addon:
```powershell
heroku login
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
```
2. Add a `Procfile` to repo root:
```
web: gunicorn mysite.wsgi --log-file -
```
3. Add `runtime.txt` (optional) to pin Python version, e.g. `python-3.11.6`.
4. Ensure `requirements.txt` is up to date: `pip freeze > requirements.txt`.
5. Configure Heroku env vars (SECRET_KEY, DEBUG=False, DJANGO_ALLOWED_HOSTS):
```powershell
heroku config:set DJANGO_SECRET_KEY="<your-secret>"
heroku config:set DJANGO_DEBUG=False
heroku config:set DJANGO_ALLOWED_HOSTS=your-app-name.herokuapp.com
```
6. If using S3 for media, add AWS env vars to Heroku as well.
7. Push to Heroku:
```powershell
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py collectstatic --noinput
```

## 13) Serve media and static
- Static: WhiteNoise serves static assets when configured; Heroku will run `collectstatic` and WhiteNoise will serve from `STATIC_ROOT`.
- Media (user uploads): Use S3 (recommended) or serve from an attached storage if your host supports it.

## 14) Verify the app
- Open `https://your-app-name.herokuapp.com` and test signup/login, create transactions, and file uploads.

## 15) Security checklist before sharing link on resume
- Set `DEBUG=False` in production and configure `ALLOWED_HOSTS`.
- Use strong `DJANGO_SECRET_KEY` in env vars.
- Ensure you did not commit `.env` or secrets to GitHub.
- Use HTTPS (Heroku provides TLS by default).

---


    ## Useful local / deploy commands (PowerShell)
    ```powershell
    # Local dev
    .\.venv\Scripts\Activate
    pip install -r requirements.txt
    py manage.py migrate
    py manage.py runserver

    # Prepare for deploy
    pip freeze > requirements.txt
    git add .
    git commit -m "ready for deploy"

    # Push to GitHub
    git push origin main

    # Push to Heroku (after heroku create)
    git push heroku main
    heroku run python manage.py migrate
    heroku run python manage.py collectstatic --noinput
    ```

    ## Environment variables you should define (example keys)
    - DJANGO_SECRET_KEY
    - DJANGO_DEBUG (True/False)
    - DJANGO_ALLOWED_HOSTS (comma-separated hostnames)
    - DATABASE_URL (if using Heroku Postgres or external DB)
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
    - AWS_STORAGE_BUCKET_NAME
    - USE_S3 (True/False)

    ## Finish
    This document should let you and other contributors set up the project locally and deploy it to Heroku using GitHub for source control. If you want, I can also add a small GitHub Actions workflow to automatically deploy to Heroku on push to `main`.
    ## 15) Security checklist before sharing link on resume
    - Set `DEBUG=False` in production and configure `ALLOWED_HOSTS`.
    - Use strong `DJANGO_SECRET_KEY` in env vars.
    - Ensure you did not commit `.env` or secrets to GitHub.
    - Use HTTPS (Heroku provides TLS by default).

    ---

    ## Useful local / deploy commands (PowerShell)
    ```powershell
    # Local dev
    .\.venv\Scripts\Activate
    pip install -r requirements.txt
    py manage.py migrate
    py manage.py runserver

    # Prepare for deploy
    pip freeze > requirements.txt
    git add .
    git commit -m "ready for deploy"

    # Push to GitHub
    git push origin main

    # Push to Heroku (after heroku create)
    git push heroku main
    heroku run python manage.py migrate
    heroku run python manage.py collectstatic --noinput
    ```

    ## Environment variables you should define (example keys)
    - DJANGO_SECRET_KEY
    - DJANGO_DEBUG (True/False)
    - DJANGO_ALLOWED_HOSTS (comma-separated hostnames)
    - DATABASE_URL (if using Heroku Postgres or external DB)
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
    - AWS_STORAGE_BUCKET_NAME
    - USE_S3 (True/False)

    ## Finish
    This document should let you and other contributors set up the project locally and deploy it to Heroku using GitHub for source control. If you want, I can also add a small GitHub Actions workflow to automatically deploy to Heroku on push to `main`.