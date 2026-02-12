# Generated manually to fix missing column in production
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_category_description_ar_category_description_en_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='is_published',
            field=models.BooleanField(default=True, verbose_name='منشور'),
        ),
    ]
