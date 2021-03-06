# Generated by Django 3.2.6 on 2021-08-15 15:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_celery_beat', '0015_edit_solarschedule_events_choices'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scraper', '0002_auto_20210815_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='periodic_task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='django_celery_beat.periodictask', verbose_name='periodic task'),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('feed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scraper.feed', verbose_name='feed')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
        migrations.AddField(
            model_name='feed',
            name='users',
            field=models.ManyToManyField(related_name='feeds', through='scraper.Subscription', to=settings.AUTH_USER_MODEL, verbose_name='users'),
        ),
    ]
