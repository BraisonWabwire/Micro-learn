# Generated by Django 5.1.4 on 2025-02-19 06:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Instructor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('instructor_number', models.CharField(editable=False, max_length=10, unique=True)),
                ('department', models.CharField(choices=[('CS', 'Computer Science'), ('ECE', 'Electronics & Communication'), ('ME', 'Mechanical Engineering')], max_length=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='instructor', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
