"""
WSGI config for django_crud_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_crud_project.settings")

application = get_wsgi_application()

# Auto-run migrations on Vercel (creates tables in /tmp/db.sqlite3)
if os.environ.get('VERCEL'):
    try:
        from django.core.management import call_command
        call_command('migrate', '--run-syncdb', '--noinput', verbosity=0)
    except Exception as e:
        import sys
        print(f"Migration warning: {e}", file=sys.stderr)

app = application
