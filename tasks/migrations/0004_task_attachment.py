# Generated by Django 5.1.8 on 2025-04-03 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='attachments/'),
        ),
    ]
