from datetime import timedelta
from unittest import mock
from unittest.mock import Mock

from django.conf import settings
from django.forms import model_to_dict
from django.test import TestCase
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from apps.authentication.models import User
from apps.authentication.tests import SAMPLE_USER
from apps.scraper.models import Item, Feed
from apps.scraper.tests import SAMPLE_FEED, SAMPLE_ITEMS


class FeedModelTestCase(TestCase):
    def setUp(self):
        self.maxDiff = 10000

    @mock.patch('apps.scraper.rss.parse_url')
    def test_update_items(self, mock_parse_url: Mock):
        mock_parse_url.return_value = (SAMPLE_FEED.copy(), SAMPLE_ITEMS.copy())

        url = 'https://test.com'
        feed = Feed(url=url, **SAMPLE_FEED)
        feed.update_items()

        mock_parse_url.assert_called_once_with(url)
        output_item_dicts = []
        for item in Item.objects.all():
            item_dict = model_to_dict(item)
            del item_dict['id']
            del item_dict['feed']
            del item_dict['viewers']
            output_item_dicts.append(item_dict)

        self.assertListEqual(
            output_item_dicts,
            SAMPLE_ITEMS
        )

    @mock.patch('apps.scraper.rss.parse_url')
    @mock.patch('apps.scraper.models.Feed.update_items')
    def test_create_from_url(self, mock_update_items: Mock, mock_parse_url: Mock):
        mock_parse_url.return_value = (SAMPLE_FEED.copy(), SAMPLE_ITEMS.copy())
        url = 'https://test.com'
        feed = Feed.objects.create_from_url(url)

        mock_parse_url.assert_called_once_with(url)
        mock_update_items.assert_called_once()

        output_feed_dict = model_to_dict(feed)
        for key in ['id', 'url', 'periodic_task', 'users']:
            del output_feed_dict[key]
        self.assertDictEqual(
            output_feed_dict,
            SAMPLE_FEED
        )

        self.assertIsInstance(feed.periodic_task, PeriodicTask)
        self.assertIsInstance(feed.periodic_task.interval, IntervalSchedule)
        self.assertEqual(feed.interval, feed.expected_ttl)
        self.assertEqual(feed.periodic_task.task, 'apps.scraper.tasks.update_feed')
        self.assertEqual(feed.periodic_task.args, f'[{feed.id}]')

    def test_expected_ttl_getter_fallback(self):
        feed = Feed()
        self.assertEqual(feed.expected_ttl, settings.DIGICLOUD_DEFAULT_FEED_UPDATE_INTERVAL)

    def test_expected_ttl_getter_using_ttl(self):
        feed = Feed(
            ttl=timedelta(seconds=30)
        )
        self.assertEqual(feed.expected_ttl, timedelta(seconds=30))

    def test_interval_getter(self):
        task = PeriodicTask()
        task.interval = IntervalSchedule(
            every=30,
            period=IntervalSchedule.SECONDS,
        )
        feed = Feed(periodic_task=task)
        self.assertEqual(feed.interval, timedelta(seconds=30))

    def test_interval_setter(self):
        task = PeriodicTask()
        task.interval = IntervalSchedule(
            every=60,
            period=IntervalSchedule.SECONDS,
        )
        feed = Feed(periodic_task=task)
        feed.interval = timedelta(seconds=60)
        self.assertEqual(task.interval.every, 60)

    def test_for_user_scope(self):
        user = User.objects.create_user(**SAMPLE_USER)
        allowed_feed = Feed.objects.create(url='https://test.com', **SAMPLE_FEED)
        disallowed_feed = Feed.objects.create(url='https://test2.com', **SAMPLE_FEED)
        allowed_feed.users.add(user)

        allowed_feeds = Feed.objects.for_user(user).all()
        self.assertListEqual(list(allowed_feeds), [allowed_feed])
