# Generated by Django 3.2.6 on 2021-08-14 13:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(verbose_name='url')),
                ('title', models.TextField(verbose_name='title')),
                ('link', models.URLField(verbose_name='link')),
                ('description', models.TextField(verbose_name='description')),
                ('language', models.CharField(blank=True, max_length=32, null=True, verbose_name='language')),
                ('copyright', models.TextField(blank=True, null=True, verbose_name='copyright')),
                ('managingEditor', models.TextField(blank=True, null=True, verbose_name='managing editor')),
                ('webMaster', models.TextField(blank=True, null=True, verbose_name='web master')),
                ('pubDate', models.DateTimeField(blank=True, null=True, verbose_name='web pubDate')),
                ('lastBuildDate', models.DateTimeField(blank=True, null=True, verbose_name='web pubDate')),
                ('categories', models.JSONField(default=list, verbose_name='categories')),
                ('generator', models.TextField(blank=True, null=True, verbose_name='generator')),
                ('ttl', models.DurationField(blank=True, null=True, verbose_name='time to live')),
                ('image', models.JSONField(default=dict, verbose_name='image')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(blank=True, null=True, verbose_name='title')),
                ('link', models.URLField(blank=True, null=True, verbose_name='link')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('author', models.TextField(blank=True, null=True, verbose_name='author')),
                ('categories', models.JSONField(default=list, verbose_name='categories')),
                ('comments', models.URLField(blank=True, null=True, verbose_name='comments')),
                ('enclosure', models.JSONField(default=dict, verbose_name='enclosure')),
                ('guid', models.CharField(blank=True, db_index=True, max_length=4096, null=True, verbose_name='guid')),
                ('pubDate', models.DateTimeField(blank=True, null=True, verbose_name='web pubDate')),
                ('feed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='scraper.feed', verbose_name='feed')),
            ],
        ),
    ]
