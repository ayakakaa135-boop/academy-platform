from django.db import migrations

def set_site_name(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    # Update the default site (ID=1)
    Site.objects.update_or_create(
        id=1,
        defaults={
            'domain': 'academy-platform.onrender.com',
            'name': 'الأكاديمية التعليمية'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(set_site_name),
    ]
