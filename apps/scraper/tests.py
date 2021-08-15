from datetime import timedelta
from email.utils import parsedate_to_datetime

from django.test import TestCase

from bs4 import BeautifulSoup

from apps.scraper.rss import _parse_categories, _parse_image, _PARSER_NAME, _parse_content, _parse_enclosure


class RssParserTestCase(TestCase):
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
        data = """
<?xml version="1.0" encoding="windows-1252"?>
<rss version="2.0">
    <channel>
        <title>FeedForAll Sample Feed</title>
        <description>RSS is a fascinating technology. The uses for RSS are expanding daily. Take a closer look at how various industries are using the benefits of RSS in their businesses.</description>
        <link>http://www.feedforall.com/industry-solutions.htm</link>
        <category domain="www.dmoz.com">Computers/Software/Internet/Site Management/Content Management</category>
        <copyright>Copyright 2004 NotePage, Inc.</copyright>
        <docs>http://blogs.law.harvard.edu/tech/rss</docs>
        <language>en-us</language>
        <lastBuildDate>Tue, 19 Oct 2004 13:39:14 -0400</lastBuildDate>
        <managingEditor>marketing@feedforall.com</managingEditor>
        <pubDate>Tue, 19 Oct 2004 13:38:55 -0400</pubDate>
        <webMaster>webmaster@feedforall.com</webMaster>
        <generator>FeedForAll Beta1 (0.0.1.8)</generator>
        <ttl>720</ttl>
        <image>
            <url>http://www.feedforall.com/ffalogo48x48.gif</url>
            <title>FeedForAll Sample Feed</title>
            <link>http://www.feedforall.com/industry-solutions.htm</link>
            <description>FeedForAll Sample Feed</description>
            <width>48</width>
            <height>48</height>
        </image>
        <item>
            <title>RSS Solutions for Restaurants</title>
            <description>&lt;b&gt;FeedForAll &lt;/b&gt;helps Restaurant&apos;s communicate with customers. Let your customers know the latest specials or events.&lt;br&gt;
&lt;br&gt;
RSS feed uses include:&lt;br&gt;
&lt;i&gt;&lt;font color=&quot;#FF0000&quot;&gt;Daily Specials &lt;br&gt;
Entertainment &lt;br&gt;
Calendar of Events &lt;/i&gt;&lt;/font&gt;</description>
            <link>http://www.feedforall.com/restaurant.htm</link>
            <category domain="www.dmoz.com">Computers/Software/Internet/Site Management/Content Management</category>
            <comments>http://www.feedforall.com/forum</comments>
            <pubDate>Tue, 19 Oct 2004 11:09:11 -0400</pubDate>
            <author>John Doe</author>
            <enclosure url="http://www.feedforall.com/restaurant.mp3" length="6974152" type="audio/mp3" />
            <guid isPermalink="true">http://www.feedforall.com/restaurant.htm</guid>
        </item>
        <item>
            <title>RSS Solutions for Schools and Colleges</title>
            <description>FeedForAll helps Educational Institutions communicate with students about school wide activities, events, and schedules.&lt;br&gt;
&lt;br&gt;
RSS feed uses include:&lt;br&gt;
&lt;i&gt;&lt;font color=&quot;#0000FF&quot;&gt;Homework Assignments &lt;br&gt;
School Cancellations &lt;br&gt;
Calendar of Events &lt;br&gt;
Sports Scores &lt;br&gt;
Clubs/Organization Meetings &lt;br&gt;
Lunches Menus &lt;/i&gt;&lt;/font&gt;</description>
            <link>http://www.feedforall.com/schools.htm</link>
            <category domain="www.dmoz.com">Computers/Software/Internet/Site Management/Content Management</category>
            <comments>http://www.feedforall.com/forum</comments>
            <pubDate>Tue, 19 Oct 2004 11:09:09 -0400</pubDate>
            <author>John Doe</author>
            <enclosure url="http://www.feedforall.com/schools.mp3" length="8123351" type="audio/mp3" />
            <guid isPermalink="true">http://www.feedforall.com/schools.htm</guid>
        </item>
    </channel>
</rss>
"""
        expected_feed = {
            'title': 'FeedForAll Sample Feed',  # noqa
            'link': 'http://www.feedforall.com/industry-solutions.htm',
            'description': "RSS is a fascinating technology. The uses for RSS are expanding daily. Take a closer look at "
                        "how various industries are using the benefits of RSS in their businesses.",
            'language': 'en-us',
            'copyright': 'Copyright 2004 NotePage, Inc.',
            'managingEditor': 'marketing@feedforall.com',
            'webMaster': 'webmaster@feedforall.com',
            'pubDate': parsedate_to_datetime('Tue, 19 Oct 2004 13:38:55 -0400'),
            'lastBuildDate': parsedate_to_datetime('Tue, 19 Oct 2004 13:39:14 -0400'),
            'categories': [
                {
                    'title': 'Computers/Software/Internet/Site Management/Content Management',
                    'domain': 'www.dmoz.com',
                }
            ],
            'generator': 'FeedForAll Beta1 (0.0.1.8)',
            'ttl': timedelta(minutes=720),
            'image': {
                'url': 'http://www.feedforall.com/ffalogo48x48.gif',
                'title': 'FeedForAll Sample Feed',
                'link': 'http://www.feedforall.com/industry-solutions.htm',
                'description': 'FeedForAll Sample Feed',
                'width': 48,
                'height': 48,
            },
        }
        expected_items = [
            {
                'title': 'RSS Solutions for Restaurants',
                'description': """<b>FeedForAll </b>helps Restaurant\'s communicate with customers. Let your customers know the latest specials or events.<br>
<br>
RSS feed uses include:<br>
<i><font color="#FF0000">Daily Specials <br>
Entertainment <br>
Calendar of Events </i></font>""",
                'link': 'http://www.feedforall.com/restaurant.htm',
                'categories': [
                    {
                        'title': 'Computers/Software/Internet/Site Management/Content Management',
                        'domain': 'www.dmoz.com',
                    }
                ],
                'comments': 'http://www.feedforall.com/forum',
                'pubDate': parsedate_to_datetime('Tue, 19 Oct 2004 11:09:11 -0400'),
                'author': 'John Doe',
                'enclosure': {
                    'url': 'http://www.feedforall.com/restaurant.mp3',
                    'length': 6974152,
                    'type': 'audio/mp3',
                },
                'guid': 'http://www.feedforall.com/restaurant.htm',
            },
            {
                'title': 'RSS Solutions for Schools and Colleges',
                'description': """FeedForAll helps Educational Institutions communicate with students about school wide activities, events, and schedules.<br>
<br>
RSS feed uses include:<br>
<i><font color="#0000FF">Homework Assignments <br>
School Cancellations <br>
Calendar of Events <br>
Sports Scores <br>
Clubs/Organization Meetings <br>
Lunches Menus </i></font>""",
                'link': 'http://www.feedforall.com/schools.htm',
                'categories': [
                    {
                        'title': 'Computers/Software/Internet/Site Management/Content Management',
                        'domain': 'www.dmoz.com',
                    }
                ],
                'comments': 'http://www.feedforall.com/forum',
                'pubDate': parsedate_to_datetime('Tue, 19 Oct 2004 11:09:09 -0400'),
                'author': 'John Doe',
                'enclosure': {
                    'url': 'http://www.feedforall.com/schools.mp3',
                    'length': 8123351,
                    'type': 'audio/mp3',
                },
                'guid': 'http://www.feedforall.com/schools.htm',
            },
        ]

        output_feed, output_items = _parse_content(data)

        self.maxDiff = 10000
        self.assertDictEqual(
            output_feed,
            expected_feed
        )
        self.assertListEqual(
            output_items,
            expected_items
        )
