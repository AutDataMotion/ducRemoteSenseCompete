# Generated by Django 2.1.2 on 2019-05-13 02:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RSCompeteAPI', '0005_auto_20190513_0239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='invite_code',
            field=models.CharField(max_length=4, unique=True),
        ),
    ]