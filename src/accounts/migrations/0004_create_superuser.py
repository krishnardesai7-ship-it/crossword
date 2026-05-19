from django.db import migrations

def create_superuser(apps, schema_editor):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(email='admin@crossword.com').exists() and not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            email='admin@crossword.com',
            username='admin',
            password='adminpassword123',
            first_name='Admin',
            last_name='User',
            gender='MALE'
        )

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_newuser_phone_number'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
