# Generated by Django 5.0.8 on 2024-08-26 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scc', '0002_remove_registration_conpassword'),
    ]

    operations = [
        migrations.CreateModel(
            name='admin_login',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]