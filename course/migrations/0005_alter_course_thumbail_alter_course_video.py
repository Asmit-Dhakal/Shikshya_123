# Generated by Django 4.2.16 on 2024-09-17 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0004_course_thumbail_alter_course_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='thumbail',
            field=models.FileField(blank=True, null=True, upload_to='thumbailphoto/'),
        ),
        migrations.AlterField(
            model_name='course',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='coursevideo/'),
        ),
    ]
