# Generated by Django 4.2.2 on 2023-06-11 17:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0002_alter_employeedetails_join_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employeeeducation',
            name='certificates',
        ),
    ]
