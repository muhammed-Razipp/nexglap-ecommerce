# Generated by Django 5.1.4 on 2025-05-23 06:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile1', '0002_rename_profile1_add_address'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('location', models.CharField(blank=True, max_length=200, null=True)),
                ('city', models.CharField(max_length=200)),
                ('pincode', models.IntegerField(blank=True, null=True)),
                ('phone', models.CharField(blank=True, max_length=10, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='add_address',
        ),
    ]
