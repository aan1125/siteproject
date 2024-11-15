# Generated by Django 5.1.1 on 2024-10-14 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100, unique=True)),
                ('nickname', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=20)),
                ('postcode', models.CharField(max_length=10)),
                ('address', models.CharField(max_length=200)),
                ('detail_address', models.CharField(blank=True, max_length=200)),
                ('extra_address', models.CharField(blank=True, max_length=200)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]