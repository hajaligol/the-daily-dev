# The Daily Dev

A vintage-newspaper-themed developer blog built with Django. The public
site is a multi-page, server-rendered newspaper: a blackletter masthead,
engraved illustrations, an aged-paper broadsheet grid, and editorial
articles managed entirely through the Django admin.

This README describes the project as it actually exists today, including
its production deployment path. The visual design — colors, typography,
layout, illustrations, grain/foxing texture, custom cursors, and page
transitions — is a fixed product requirement and was intentionally left
untouched by the engineering work described below.

![Screenshot](images/dd-homepage.png)

## Architecture

```
config/            Project settings, root URLconf, WSGI/ASGI entry points
newsroom/           Front page, contact page, ContactMessage model/admin
articles/           Article model/admin/views, sitemap, migrations
templates/          Project-wide base template, partials, error pages
  base.html          Shared <head>/masthead/meta-row/scripts for every page
  partials/          masthead.html, site_footer.html (reused across pages)
  404.html, 500.html Newspaper-styled error pages
  robots.txt
newsroom/templates/newsroom/   index.html, contact.html
articles/templates/articles/   article_list.html, article_detail.html
static/             css/, js/, images/ — the design's actual assets
media/              User/editor-uploaded content (article illustrations)
```

**App boundaries:** `newsroom` owns the front page and the contact
form/mailbox; `articles` owns everything about an `Article` — model, admin,
views, URLs, and its sitemap entries.

**Templates:** every page extends `templates/base.html`, which owns the
`<head>`, the masthead, the volume/date strip, and the page-transition
script include. Pages only provide their own `content` block plus small
title/description overrides. The masthead and the "blog-style" footer
(hand illustrations + page number) are further factored into
`templates/partials/` since they're byte-for-byte identical across pages.
This is a refactor for maintainability only — the rendered HTML is the
same structure as before.

## Content model

- **Article** — title, slug, category, excerpt, `content` (HTML body),
  topics, image, page reference, ordering, publish flag. `content` is
  written by trusted staff through the Django admin as simple HTML
  (`<p>`, `<h2 class="article-section-title">`,
  `<blockquote class="article-pullquote">`, `<ul>`, etc.), including one
  `[[HERO_IMAGE:caption]]` token marking where the hero image caption
  comes from.
- **ContactMessage** — created by the public contact form; read-only in
  the admin (messages can only arrive through the form, never be added
  there directly).

### Article content is sanitized, not blindly trusted

`Article.content_html` (rendered with `|safe` in `article_detail.html`)
passes the raw `content` field through an allow-list HTML sanitizer
(`nh3`, see `articles/models.py`) before rendering. Only the tags and
attributes the editorial HTML actually uses are permitted; `<script>`
tags, inline event handlers, and `javascript:` URLs are stripped. Since
`content` is only ever edited by staff through the admin, this is
defense-in-depth rather than the only line of defense — but it means a
compromised or careless admin account can no longer turn the content
field into a stored-XSS vector. See `articles/tests.py` for the tests
covering this directly.

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env if you want — the defaults (DJANGO_DEBUG=true, a placeholder
# SECRET_KEY) are fine for local development out of the box.

python manage.py migrate
python manage.py createsuperuser   # to use /admin/
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the front page, `/article/` for the
article listing, `/contact/` for the contact page, and `/admin/` to manage
articles and read contact messages.

By default (no `DATABASE_URL` set) this uses the project's SQLite file,
exactly as before. `SECRET_KEY` **must** be set once `DJANGO_DEBUG` is
false — the app fails fast with a clear error rather than silently running
insecurely (see `config/settings.py`).

## Environment variables

All of these are documented with defaults and comments in `.env.example`.

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django's cryptographic secret key. Required when `DJANGO_DEBUG` is false. |
| `DJANGO_DEBUG` | `true`/`false`. Must be `false` in any publicly reachable environment. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames Django will serve. |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated scheme+host origins allowed to submit forms (needed for HTTPS deployments). |
| `DATABASE_URL` | `postgres://user:pass@host:5432/dbname` in production; unset for local SQLite. |
| `DJANGO_SECURE_SSL_REDIRECT` | Force HTTP→HTTPS redirects. |
| `DJANGO_SESSION_COOKIE_SECURE` / `DJANGO_CSRF_COOKIE_SECURE` | Send cookies only over HTTPS. |
| `DJANGO_SECURE_HSTS_SECONDS` | HSTS max-age; `0` disables it. |
| `DJANGO_USE_X_FORWARDED_PROTO` | Enable when behind a TLS-terminating reverse proxy. |
| `DJANGO_LOG_LEVEL` | Root/`django` logger level (default `INFO`). |
| `EMAIL_*`, `DEFAULT_FROM_EMAIL` | SMTP configuration for the optional contact-form notification. |
| `CONTACT_NOTIFICATION_EMAIL` | If set, a plain-text email is sent here on every successful contact-form submission. Left blank, no email is ever sent — the message is still saved and visible in the admin. |

## Database

Local development uses SQLite (`db.sqlite3`, git-ignored) unless
`DATABASE_URL` is set. Production is expected to use PostgreSQL — set
`DATABASE_URL` and no application code changes are needed; the same
`config/settings.py` handles both via `dj-database-url`.

### Migrations and seed data

`articles/migrations/` seeds the six launch articles and their editorial
copy (`0002_seed_articles`, `0004_seed_article_content`,
`0005_rebalance_hero_placement`). **`0006_fix_seeded_image_paths`** is a
corrective migration: `0002` originally pointed five of those six articles
at SVG illustrations (`debugging-engraving.svg` and similar) that were
never actually committed to the repository — they were superseded during
development by the real `.webp` illustrations now in `media/articles/`,
but the seed migration itself was never corrected, so a fresh database
built purely from `migrate` would have rendered broken article images.
`0006` repairs this at the migration level (matching on the specific
stale path, so it's a no-op against a database where an editor has since
uploaded something else). `articles/tests.py` has a regression test
asserting no seeded article still points at the old broken paths.

Running `python manage.py migrate` against an empty database reproduces
the full, working site — no manual data-fixing steps required.

## Static and media files

- **Static** (`static/css`, `static/js`, `static/images`) is collected
  with `python manage.py collectstatic` into `STATIC_ROOT`
  (`staticfiles/`, git-ignored) and served in production via
  **WhiteNoise** with compressed, hashed filenames
  (`CompressedManifestStaticFilesStorage`) — no separate static file
  server or CDN is required to get correct caching headers.
- **Media** (`media/articles/`) holds the article illustrations, uploaded
  through the admin's `ImageField`. In development these are served by
  Django itself; WhiteNoise does not serve user-uploaded media. In
  production, mount a persistent volume at `MEDIA_ROOT` (the Docker setup
  below does this) and serve it from your reverse proxy, or swap in an
  object-storage backend (e.g. `django-storages` + S3) by changing the
  `"default"` entry in `STORAGES` — no other code changes are required.

## Running tests

```bash
python manage.py test
```

The suite (`articles/tests.py`, `newsroom/tests.py`) covers: published vs.
unpublished article visibility, slug/404 behavior, previous/next/related
article ordering, reading time and table-of-contents extraction, HTML
sanitization of article content (script tags, event handlers,
`javascript:` URLs, disallowed tags), the seeded-image-path regression
described above, contact form validation (required fields, invalid email,
whitespace trimming), CSRF enforcement, the optional email notification,
and that the success message never claims an email was sent unless one
actually was. It does not test CSS/visual rendering — see "Visual
preservation" in the engineering notes below for how that was verified
instead.

## Production checks

```bash
python manage.py check
python manage.py check --deploy
python manage.py makemigrations --check --dry-run
```

`check --deploy` validates the production security settings described
above (HSTS, secure cookies, `DEBUG`, etc.) against whatever environment
variables are set.

## Deployment

### Docker (recommended)

```bash
docker build -t daily-dev .
docker run --rm -p 8000:8000 \
  -e SECRET_KEY=... \
  -e DJANGO_ALLOWED_HOSTS=yourdomain.example \
  -e DATABASE_URL=postgres://user:pass@host:5432/dbname \
  -v daily-dev-media:/app/media \
  daily-dev
```

The image runs as a non-root user, and `docker-entrypoint.sh` runs
`migrate` and `collectstatic` automatically on every container start
before starting **Gunicorn**. A `HEALTHCHECK` hits `/healthz/`.

`docker-compose.yml` runs the app against a local PostgreSQL container —
useful for exercising the production database path before deploying:

```bash
docker compose up --build
```

### Without Docker

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

Put a reverse proxy (nginx, Caddy, your platform's load balancer, etc.) in
front of Gunicorn to terminate TLS and serve `MEDIA_ROOT` directly; static
files are already served efficiently by WhiteNoise from within the app
itself.

### CI

`.github/workflows/ci.yml` runs on every push/PR: installs dependencies
against a real PostgreSQL service container, runs `manage.py check`,
`check --deploy`, a migrations-drift check, the test suite, and
`collectstatic`.

## Admin / editorial workflow

- Articles: `/admin/articles/article/`. Slug auto-fills from the title,
  image previews are shown in both the list and the change form, `order`
  and `is_published` are editable inline from the list view, and fields
  are grouped into Editorial / Article body / Image / Placement /
  Timestamps sections.
- Contact messages: `/admin/newsroom/contactmessage/` — read-only (they
  can only be created by the public form), searchable, filterable by
  date.

## Troubleshooting

- **"SECRET_KEY environment variable must be set..."** — you're running
  with `DJANGO_DEBUG=false` (or it defaulted to false because it wasn't
  set at all) without a `SECRET_KEY`. Either set `DJANGO_DEBUG=true` for
  local development or provide a real `SECRET_KEY`.
- **Article images 404 on a fresh database** — make sure `media/` was
  checked out from the repository (these seed illustrations are committed,
  unlike `db.sqlite3`) and that `0006_fix_seeded_image_paths` has run
  (`python manage.py showmigrations articles`).
- **Static files look unstyled after deploying** — run
  `python manage.py collectstatic --noinput`; WhiteNoise serves from
  `STATIC_ROOT`, not `static/` directly, once `DEBUG` is false.

## Design preservation note

This codebase went through an architecture/security/deployment refactor
without changing the public-facing design. `static/css/style.css` and
`static/js/*.js` were **not modified**. Every template's DOM structure,
classes, and rendered copy were preserved exactly — the refactor only
introduced `{% extends %}`/`{% include %}` template inheritance around
the same markup, plus sanitization of admin-authored article HTML.
Anyone extending this project should treat the visual design the same
way: a fixed product requirement, not something to "clean up" alongside
backend changes.
