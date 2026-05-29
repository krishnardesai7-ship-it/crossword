"""
accounts/signals.py

Automatically syncs every accounts.NewUser save into the legacy
myapp.register model so the admin panel always shows up-to-date data
without needing a manual trigger.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='accounts.NewUser')
def auto_sync_register_user(sender, instance, created, **kwargs):
    """
    After any NewUser save (create or update), mirror the data into
    myapp.register so it stays consistent.
    Only syncs active users so unverified/pending registrations are skipped.
    """
    if not instance.is_active:
        return
    try:
        from myapp.models import register as RegisterUser

        gender_map = {'MALE': 'Male', 'FEMALE': 'Female'}
        gender_value = gender_map.get((instance.gender or '').upper(), '')
        full_name = f"{instance.first_name or ''} {instance.last_name or ''}".strip()

        RegisterUser.objects.update_or_create(
            email=instance.email,
            defaults={
                'username': instance.username,
                'password': instance.password,
                'confirm_password': instance.password,
                'gender': gender_value,
                'phone': instance.phone_number or '',
                'address': instance.country or '',
                's_name': full_name,
            }
        )
    except Exception as e:
        print(f"[auto_sync_register_user] Failed for {instance.email}: {e}")
