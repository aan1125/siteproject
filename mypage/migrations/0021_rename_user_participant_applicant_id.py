# Generated by Django 5.1.1 on 2024-11-13 03:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mypage', '0020_participant'),
    ]

    operations = [
        migrations.RenameField(
            model_name='participant',
            old_name='user',
            new_name='applicant_id',
        ),
    ]