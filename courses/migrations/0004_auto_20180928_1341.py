# Generated by Django 2.0.6 on 2018-09-28 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_auto_20180928_1335'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quiz',
            name='subject',
        ),
        migrations.RemoveField(
            model_name='text',
            name='subject',
        ),
        migrations.AddField(
            model_name='course',
            name='subject',
            field=models.CharField(default='', max_length=100),
        ),
    ]
