from django.db import migrations

def populate_checkout_images(apps, schema_editor):
    Checkout = apps.get_model('myapp', 'checkout')
    Product = apps.get_model('myapp', 'product')
    for order in Checkout.objects.all():
        if not order.image or order.image == 'None' or order.image == '':
            # Find a product with the same name (case-insensitive)
            prod = Product.objects.filter(name__iexact=order.product_name).first()
            if prod and prod.image:
                order.image = prod.image.name
                order.save()

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0018_load_initial_products'),
    ]

    operations = [
        migrations.RunPython(populate_checkout_images),
    ]
