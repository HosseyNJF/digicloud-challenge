# Generated by Django 3.2.6 on 2021-08-15 22:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scraper', '0003_auto_20210815_1552'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_seen', models.DateTimeField(auto_now_add=True, null=True, verbose_name='date seen')),
                ('date_bookmarked', models.DateTimeField(blank=True, null=True, verbose_name='date bookmarked')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='comment')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='interactions', to='scraper.item', verbose_name='item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='viewers',
            field=models.ManyToManyField(related_name='interacted_items', through='scraper.Interaction', to=settings.AUTH_USER_MODEL),
        ),
    ]
