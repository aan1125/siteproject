# Generated by Django 5.1.1 on 2024-11-09 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mypage', '0007_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_image_url',
            field=models.URLField(default=2),
            preserve_default=False,
        ),
    ]