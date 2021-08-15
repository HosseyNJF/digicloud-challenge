from bs4 import BeautifulSoup
from django.test import TestCase

from apps.scraper.rss import _parse_categories, _parse_image, _PARSER_NAME, _parse_content, _parse_enclosure
from apps.scraper.tests import SAMPLE_XML, SAMPLE_FEED, SAMPLE_ITEMS


class RssParserTestCase(TestCase):
    def setUp(self):
        self.maxDiff = 10000

    def test_parse_categories(self):
        data = """
        <channel>
            <category>Technology/Programming</category>
            <category>Technology</category>
            <category domain="https://digicloud.ir/tags">Technology</category>
            <category domain="https://digicloud.ir/tags">Computers</category>
        </channel>
        """
        expected = [
            {
                'title': 'Technology/Programming',
                'domain': None,
            },
            {
                'title': 'Technology',
                'domain': None,
            },
            {
                'title': 'Technology',
                'domain': 'https://digicloud.ir/tags',
            },
            {
                'title': 'Computers',
                'domain': 'https://digicloud.ir/tags',
            },
        ]
        self.assertListEqual(
            _parse_categories(BeautifulSoup(data, _PARSER_NAME).findAll('category')),
            expected
        )

    def test_parse_image_only_required(self):
        data = """
        <image>
            <url>https://google.com/test.png</url>
            <title>Google</title>
            <link>https://google.com</link>
        </image>
        """
        expected = {
            'url': 'https://google.com/test.png',
            'title': 'Google',
            'link': 'https://google.com',
            'width': None,
            'height': None,
            'description': None,
        }
        self.assertDictEqual(
            _parse_image(BeautifulSoup(data, _PARSER_NAME).find('image')),
            expected
        )

    def test_parse_image_with_optional(self):
        data = """
        <image>
            <url>https://google.com/test.png</url>
            <title>Google</title>
            <link>https://google.com</link>
            <width>1024</width>
            <height>768</height>
            <description>Google's logo</description>
        </image>
        """
        expected = {
            'url': 'https://google.com/test.png',
            'title': 'Google',
            'link': 'https://google.com',
            'width': 1024,
            'height': 768,
            'description': "Google's logo",
        }
        self.assertDictEqual(
            _parse_image(BeautifulSoup(data, _PARSER_NAME).find('image')),
            expected
        )

    def test_parse_enclosure(self):
        data = """
        <enclosure url="http://google.com/hello.mp3" length="5100000" type="audio/mp3" />
        """
        expected = {
            'url': 'http://google.com/hello.mp3',
            'length': 5100000,
            'type': 'audio/mp3',
        }
        self.assertDictEqual(
            _parse_enclosure(BeautifulSoup(data, _PARSER_NAME).find('enclosure')),
            expected
        )

    def test_parse_content(self):
        output_feed, output_items = _parse_content(SAMPLE_XML)

        self.assertDictEqual(
            output_feed,
            SAMPLE_FEED
        )
        self.assertListEqual(
            output_items,
            SAMPLE_ITEMS
        )
