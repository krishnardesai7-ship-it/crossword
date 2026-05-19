from django.db import migrations
from django.core.management import call_command

def load_fixture(apps, schema_editor):
    try:
        call_command('loaddata', 'products.json')
    except Exception as e:
        print(f"Error loading fixture: {e}")

def unload_fixture(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0017_book'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture),
    ]
