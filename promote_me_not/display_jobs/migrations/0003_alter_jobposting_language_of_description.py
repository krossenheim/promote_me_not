# Generated by Django 4.1.2 on 2022-10-24 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('display_jobs', '0002_jobposting_job_id_jobposting_posted_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobposting',
            name='language_of_description',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]
