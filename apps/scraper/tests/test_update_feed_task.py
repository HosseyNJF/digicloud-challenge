from datetime import timedelta
from unittest import mock
from unittest.mock import Mock

from django.conf import settings
from django.test import TestCase, override_settings
from requests import RequestException

from apps.scraper.models import Feed
from apps.scraper.tasks import _update_feed, update_feed
from apps.scraper.tests import SAMPLE_FEED


class UpdateFeedTaskTestCase(TestCase):

    @mock.patch('apps.scraper.tasks._update_feed')
    def test_correct_update_task(self, mock_update_feed: Mock):
        feed = Feed.objects.create(
            url='https://test.com',
            **SAMPLE_FEED,
        )
        update_feed(feed.pk)
        mock_update_feed.assert_called_once_with(feed)

    def test_correct_update_execution(self):
        feed = Mock()
        feed.expected_ttl = timedelta(seconds=5)
        feed.interval = timedelta(seconds=5)

        _update_feed(feed)

        feed.update_items.assert_called_once()

    def test_correct_backoff_reset(self):
        feed = Mock()
        expected = timedelta(seconds=5)
        feed.expected_ttl = expected
        feed.interval = timedelta(seconds=60)

        _update_feed(feed)

        self.assertEqual(feed.interval, expected)

    @override_settings(DIGICLOUD_BACKOFF_MAXIMUM_DURATION=timedelta(seconds=60))
    @override_settings(DIGICLOUD_BACKOFF_FACTOR=2)
    def test_normal_backoff(self):
        feed = Mock()
        feed.update_items.side_effect = RequestException()
        interval = timedelta(seconds=10)
        feed.interval = interval

        _update_feed(feed)
        self.assertEqual(feed.interval, interval * settings.DIGICLOUD_BACKOFF_FACTOR)

    @override_settings(DIGICLOUD_BACKOFF_MAXIMUM_DURATION=timedelta(seconds=5))
    @override_settings(DIGICLOUD_BACKOFF_FACTOR=2)
    def test_maximum_backoff(self):
        feed = Mock()
        feed.update_items.side_effect = RequestException()
        interval = timedelta(seconds=3)  # Multiplied by 2, this should become 6 seconds but the maximum is 5
        feed.interval = interval

        _update_feed(feed)
        self.assertEqual(feed.interval, settings.DIGICLOUD_BACKOFF_MAXIMUM_DURATION)
