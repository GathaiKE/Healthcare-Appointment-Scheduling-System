# Generated by Django 5.1.7 on 2025-04-06 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
