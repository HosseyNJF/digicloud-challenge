import re
from datetime import timedelta
from email.utils import parsedate_to_datetime

import requests
from bs4 import BeautifulSoup
from lxml import etree

_PARSER_NAME = 'lxml-xml'


def _parse_categories(category_elems):
    return [
        {
            'title': category_elem.text,
            'domain': category_elem.get('domain'),
        } for category_elem in category_elems
    ]


def _parse_image(image_elem):
    return {
        'url': image_elem.url.text,
        'title': image_elem.title.text,
        'link': image_elem.link.text,
        'width': int(elem.text) if (elem := image_elem.width) and elem.text.isnumeric() else None,
        'height': int(elem.text) if (elem := image_elem.height) and elem.text.isnumeric() else None,
        'description': elem.text if (elem := image_elem.description) else None,
    }


def _parse_enclosure(enclosure_elem):
    return {
        'url': enclosure_elem['url'],
        'length': int(enclosure_elem['length']),
        'type': enclosure_elem['type'],
    }


def _parse_content(content):
    # These lines will make sure that HTML entities get decoded correctly
    dtd_str = """<?xml version="1.0"?>
<!DOCTYPE
   xml
   PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
>"""
    content = re.sub(r'<\?xml(.*?)\?>', '', content)
    tree = etree.fromstring(dtd_str + content)

    soup = BeautifulSoup(etree.tostring(tree, encoding='unicode'), "lxml-xml")
    feed = {
        'title': soup.title.text,  # noqa
        'link': soup.link.text,
        'description': soup.description.text,
        'language': elem.text if (elem := soup.language) else None,
        'copyright': elem.text if (elem := soup.copyright) else None,
        'managingEditor': elem.text if (elem := soup.managingEditor) else None,
        'webMaster': elem.text if (elem := soup.webMaster) else None,
        'pubDate': parsedate_to_datetime(elem.text) if (elem := soup.pubDate) else None,
        'lastBuildDate': parsedate_to_datetime(elem.text) if (elem := soup.lastBuildDate) else None,
        'categories': _parse_categories(soup.select('channel > category')),
        'generator': elem.text if (elem := soup.generator) else None,
        'ttl': timedelta(minutes=int(elem.text)) if (elem := soup.ttl) and elem.text.isnumeric() else None,
        'image': _parse_image(elem) if (elem := soup.image) else {},
    }
    items = [
        {
            'title': elem.text if (elem := item_elem.title) else None,
            'link': elem.text if (elem := item_elem.link) else None,
            'description': elem.string if (elem := item_elem.description) else None,
            'author': elem.text if (elem := item_elem.author) else None,
            'categories': _parse_categories(item_elem.findAll('category')),
            'comments': elem.text if (elem := item_elem.comments) else None,
            'enclosure': _parse_enclosure(elem) if (elem := item_elem.enclosure) else {},
            'guid': elem.text if (elem := item_elem.guid) else None,
            'pubDate': parsedate_to_datetime(elem.text) if (elem := item_elem.pubDate) else None,
        } for item_elem in soup.findAll('item')
    ]
    return feed, items


def parse_url(url):
    return _parse_content(requests.get(url).text)
