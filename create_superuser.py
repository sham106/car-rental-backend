import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lexuBackend.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

ADMIN_EMAIL = os.environ.get("DJANGO_ADMIN_EMAIL")
ADMIN_PASSWORD = os.environ.get("DJANGO_ADMIN_PASSWORD")

if not User.objects.filter(email=ADMIN_EMAIL).exists():
    User.objects.create_superuser(
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD
    )
    print(f"Superuser '{ADMIN_EMAIL}' created successfully!")
else:
    print(f"Superuser '{ADMIN_EMAIL}' already exists.")
