import json
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from apps.authentication.models import User
from apps.scraper import rss


class FeedManager(models.Manager):
    def create_from_url(self, url):
        feed_dict, _ = rss.parse_url(url)
        feed_dict['url'] = url
        feed = self.create(**feed_dict)
        feed.update_items()  # TODO: fix: one extra request is being made here
        feed.periodic_task = PeriodicTask(
            name=f'Update feed #{feed.pk}',
            task='apps.scraper.tasks.update_feed',
            args=json.dumps([feed.pk])
        )
        feed.interval = feed.expected_ttl
        feed.periodic_task.save()
        feed.save()
        return feed


class Feed(models.Model):
    objects = FeedManager()

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

    date_created = models.DateTimeField(
        _('date created'),
        auto_now_add=True,
    )

    # Technical fields
    @property
    def expected_ttl(self) -> timedelta:
        return self.ttl or settings.DIGICLOUD_DEFAULT_FEED_UPDATE_INTERVAL

    @property
    def interval(self) -> timedelta:
        return timedelta(seconds=self.periodic_task.interval.every)

    @interval.setter
    def interval(self, interval: timedelta):
        interval_schedule, _ = IntervalSchedule.objects.get_or_create(
            every=interval.total_seconds(),
            period=IntervalSchedule.SECONDS,
        )
        self.periodic_task.interval = interval_schedule
        self.periodic_task.save()

    users = models.ManyToManyField(
        User,
        verbose_name=_('users'),
        related_name='feeds',
        through='Subscription',
    )
    periodic_task = models.ForeignKey(
        PeriodicTask,
        verbose_name=_('periodic task'),
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
    )

    def update_items(self):
        feed_dict, item_dict_list = rss.parse_url(self.url)

        for attr, value in feed_dict.items():
            setattr(self, attr, value)
        self.save()

        # RSS doesn't define a unique field for an item, and the closest we can get is the <guid> tag. The problem
        # is that it isn't declared mandatory by the specifications, and it simply isn't reliable. We have to resort
        # to alternate and not 100% perfect solutions.

        # There are multiple approaches to finding duplicate items and preventing their re-insertion, But the
        # most straightforward and error-proof way of them is to consider their permalink as their unique ID.
        # Because most of the times, links aren't going to change. They should be considered permanent for any item.

        present_item_keys = [present_item.link for present_item in self.items.all()]
        fresh_items = []

        for item_dict in item_dict_list:
            if item_dict['link'] not in present_item_keys:
                fresh_items.append(Item(
                    feed=self,
                    **item_dict
                ))
        Item.objects.bulk_create(fresh_items)


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

    date_created = models.DateTimeField(
        _('date created'),
        auto_now_add=True,
    )


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
    )
    feed = models.ForeignKey(
        Feed,
        verbose_name=_('feed'),
        on_delete=models.CASCADE,
    )
    date_created = models.DateTimeField(
        _('date created'),
        auto_now_add=True,
    )
