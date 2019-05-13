# Generated by Django 2.1.2 on 2019-05-13 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RSCompeteAPI', '0004_result_root_dir'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='work_place',
        ),
        migrations.AddField(
            model_name='result',
            name='file_name',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AddField(
            model_name='team',
            name='invite_code',
            field=models.CharField(default='1234', max_length=4),
        ),
        migrations.AddField(
            model_name='user',
            name='work_place_second',
            field=models.CharField(default='', max_length=64),
        ),
        migrations.AddField(
            model_name='user',
            name='work_place_third',
            field=models.CharField(default='', max_length=64),
        ),
        migrations.AddField(
            model_name='user',
            name='work_place_top',
            field=models.CharField(default='', max_length=64),
        ),
        migrations.AlterField(
            model_name='user',
            name='work_id',
            field=models.IntegerField(choices=[(1, '学生'), (2, '教师'), (3, '工程师'), (4, '科研人员'), (5, '其他')]),
        ),
    ]
