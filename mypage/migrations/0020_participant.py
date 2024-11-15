# Generated by Django 5.1.1 on 2024-11-12 12:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mypage', '0019_alter_registeredproduct_courier_service_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='mypage.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
