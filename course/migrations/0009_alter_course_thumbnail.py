# Generated by Django 4.2.16 on 2024-09-24 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0008_remove_chapter_short_clip_payment_payment_gateway_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='thumbnail',
            field=models.FileField(blank=True, null=True, upload_to='thumbnail_photo/'),
        ),
    ]
