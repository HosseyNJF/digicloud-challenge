from django.db import models
from django.utils.translation import gettext_lazy as _


class Feed(models.Model):
    url = models.URLField(
        _('url'),
    )

    title = models.TextField(
        _('title'),
    )
    link = models.URLField(
        _('link'),
    )
    description = models.TextField(
        _('description'),
    )

    language = models.CharField(
        _('language'),
        max_length=32,
        blank=True,
        null=True,
    )
    copyright = models.TextField(
        _('copyright'),
        blank=True,
        null=True,
    )
    managingEditor = models.TextField(
        _('managing editor'),
        blank=True,
        null=True,
    )
    webMaster = models.TextField(
        _('web master'),
        blank=True,
        null=True,
    )
    pubDate = models.DateTimeField(
        _('web pubDate'),
        blank=True,
        null=True,
    )
    lastBuildDate = models.DateTimeField(
        _('web pubDate'),
        blank=True,
        null=True,
    )
    categories = models.JSONField(
        _('categories'),
        default=list,
    )
    generator = models.TextField(
        _('generator'),
        blank=True,
        null=True,
    )
    ttl = models.DurationField(
        _('time to live'),
        blank=True,
        null=True,
    )
    image = models.JSONField(
        _('image'),
        default=dict,
    )


class Item(models.Model):
    feed = models.ForeignKey(
        to=Feed,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('feed'),
    )
    title = models.TextField(
        _('title'),
        blank=True,
        null=True,
    )
    link = models.URLField(
        _('link'),
        blank=True,
        null=True,
    )
    description = models.TextField(
        _('description'),
        blank=True,
        null=True,
    )
    author = models.TextField(
        _('author'),
        blank=True,
        null=True,
    )
    categories = models.JSONField(
        _('categories'),
        default=list,
    )
    comments = models.URLField(
        _('comments'),
        blank=True,
        null=True,
    )
    enclosure = models.JSONField(
        _('enclosure'),
        default=dict,
    )
    guid = models.CharField(
        _('guid'),
        max_length=4096,
        db_index=True,
        blank=True,
        null=True,
    )
    pubDate = models.DateTimeField(
        _('web pubDate'),
        blank=True,
        null=True,
    )
