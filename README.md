# Picture Mapper

Register, upload pictures with the place they were taken, and see everyone's pictures on one map.

- Click the map to say where a picture was taken, or leave it blank and the location is read from the
  photo's GPS data.
- Your own pictures page, with edit and delete (you can only touch your own).
- A global map of every picture, filterable by user.
- Maps are [Leaflet](https://leafletjs.com/) with [OpenStreetMap](https://www.openstreetmap.org/) tiles: no API
  key or account. Leaflet is vendored in `static/vendor/leaflet` (version 1.9.4, BSD-2-Clause).

Django 6.1, Pillow, SQLite, uploads on local disk. Python 3.12 or newer.

## Run it locally

```
uv sync
export DJANGO_DEBUG=1
uv run python manage.py migrate
uv run python manage.py createsuperuser   # optional, for /admin/
uv run python manage.py runserver
```

## Settings

All from environment variables; nothing secret is in the repo.

| Variable | Default | |
| --- | --- | --- |
| `DJANGO_DEBUG` | off | `1` for local development. Without it the site needs the next two. |
| `DJANGO_SECRET_KEY` | none | Required when not in debug mode; startup fails without it. |
| `DJANGO_ALLOWED_HOSTS` | none | Comma separated host names. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | none | e.g. `https://pictures.example.com` if behind a proxy. |
| `DJANGO_DB_PATH` | `db.sqlite3` | SQLite file. |
| `DJANGO_MEDIA_ROOT` | `media/` | Where uploads are stored; your web server must serve `/media/`. |
| `REGISTRATION_OPEN` | `1` | `0` stops new sign-ups. |
| `MAX_UPLOAD_MB` | `10` | Largest picture. |
| `DJANGO_SSL_REDIRECT` | `1` | Redirect to HTTPS outside debug mode. |

Production: `uv run python manage.py collectstatic`, run behind a TLS-terminating proxy that sets
`X-Forwarded-Proto`, serve `/static/` (from `staticfiles/`) and `/media/` from the web server, and run
`uv run python manage.py check --deploy`.

## Development

```
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

Dependabot opens PRs only for security fixes and GitHub Actions; they merge themselves once the `check`
status passes.

## History

This is a 2013 Django 1.5 / Python 2 project rewritten from scratch. The old code is in the git history.
