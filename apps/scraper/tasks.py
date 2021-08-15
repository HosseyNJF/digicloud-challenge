from celery import shared_task
from django.conf import settings
from requests import RequestException

from apps.scraper.models import Feed


@shared_task
def update_feed(feed_pk):
    feed = Feed.objects.filter(pk=feed_pk).select_related('periodic_task__interval').first()
    _update_feed(feed)


def _update_feed(feed: Feed):
    try:
        feed.update_items()

        # Reset backoff if the request succeeds
        if (expected_ttl := feed.expected_ttl) < feed.interval:
            feed.interval = expected_ttl

    except RequestException:  # Try a simple exponential backoff mechanism
        feed.interval = min(
            feed.interval * settings.DIGICLOUD_BACKOFF_FACTOR,
            settings.DIGICLOUD_BACKOFF_MAXIMUM_DURATION
        )
