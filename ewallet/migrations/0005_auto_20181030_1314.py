# Generated by Django 2.1.2 on 2018-10-30 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ewallet', '0004_user_nama'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_id',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
