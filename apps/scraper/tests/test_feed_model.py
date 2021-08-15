from unittest import mock
from unittest.mock import Mock

from django.forms import model_to_dict
from django.test import TestCase

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
