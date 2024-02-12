"""
WSGI config for api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

application = get_wsgi_application()


def handler(event, context):
    if "_wsgi" in event:
        meta = event["_wsgi"]
        if meta.get("command") == "manage":
            # Run Django management commands
            import django
            from django.core.management import execute_from_command_line

            django.setup()
            args = meta.get("args", list())
            if args and not isinstance(args, list):
                args = args.split(" ")
            args = ["manage.py", *args]
            print("Executing Django management command ", args)
            execute_from_command_line(args)
            return [
                0,
            ]
    else:
        import serverless_wsgi  # noqa

        return serverless_wsgi.handle_request(application, event, context)
