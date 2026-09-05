# The Daily Dev

Django 5.2 / Python 3.14 project for "The Daily Dev" front page.
Currently a single static-content page, ready to be expanded with real
models/views as the project grows.

## Structure

```
config/            project settings & root urls
newsroom/           app that owns the front page
  templates/newsroom/index.html
static/
  css/style.css      (moved out of the original inline <style> block, unchanged)
  images/             all webp/svg assets from the prototype
  js/                 empty, ready for future scripts
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to see the front page.

## Notes

- The `index.html` template is the exact prototype markup, with only the
  `<style>` block extracted to `static/css/style.css` and image `src`
  attributes swapped for `{% static %}` tags. The side-column stories and
  the three-column footer stories are untouched.
- `STATICFILES_DIRS` points Django at the project-level `static/` folder
  in development; run `python manage.py collectstatic` to gather files
  into `STATIC_ROOT` (`staticfiles/`) for deployment.
