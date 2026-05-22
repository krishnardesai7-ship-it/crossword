from django.db import migrations
from django.core.management import call_command


def load_books_fixture(apps, schema_editor):
    """Load books data from fixture — runs on every fresh DB (e.g. Render deploy)."""
    Book = apps.get_model('myapp', 'Book')
    # Only load if table is empty to avoid duplicates
    if not Book.objects.exists():
        try:
            call_command('loaddata', 'books.json', verbosity=0)
        except Exception as e:
            print(f"[Migration 0020] Warning: Could not load books fixture: {e}")


def unload_books_fixture(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0019_populate_checkout_images'),
    ]

    operations = [
        migrations.RunPython(load_books_fixture, reverse_code=unload_books_fixture),
    ]
