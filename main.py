# -*- coding: utf-8 -*-
import re
import sys
import logging
import unicodedata
from urllib.parse import urljoin
from urllib.parse import urlparse

import validators
from scrapy.http import Request
from scrapy.item import Field, Item
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider
from scrapy.utils.log import configure_logging
from itemloaders.processors import Identity, MapCompose, TakeFirst

#
# Some constants
#
SETTINGS = {
    'BOT_NAME': 'cdtest',
    'ROBOTSTXT_OBEY': False,
    'CONCURRENT_REQUESTS': 8,
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
        'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
    }
}

PHONE_REGEX = re.compile(
    (r'(\+\d{1,2}\s\(?\d{1,3}\)?\s\d{3,4}\D\d{2}\D\d{2}|\+\d{1,2}\s\(?\d{1,3}\)?\s\d{3,4}\D\d{4}|\d{3}\-\d{3}\-\d{4})'))

LOGO_XPATH_TMPL = "//img[contains(%s, '%s')]/@src"


class Unique:
    """
        List to set processor
    """

    def __call__(self, values):
        return list(dict.fromkeys(values))


class ParsedItem(Item):
    """
        The item which parsed data will be loaded
    """
    website = Field(output_processor=TakeFirst())
    logo = Field(output_processor=TakeFirst())
    phones = Field(
        input_processor=MapCompose(
            lambda s: ' '.join(s.split()),  # remove extra spaces
            lambda s: unicodedata.normalize('NFKD', s)  # remove unicode chars
            .encode('ascii', 'replace')
            .decode('utf-8')
            .replace('?', ' ')),
        output_processor=Unique())


class CialDnbTestSpider(CrawlSpider):
    """
        The main spider
    """
    name = 'cialdnbtest'

    def __init__(self, start_urls, *args, **kwargs):
        self.start_urls = start_urls
        self._set_logging()

        super().__init__(*args, **kwargs)

    def _set_logging(self):
        """
            Sets to CRITICAL standard scrapy loggers, third-party loggers
            and creates a custom logger.
        """
        root = logging.getLogger()
        for h in root.handlers:
            h.setLevel(logging.CRITICAL)

        # Configure a custom logger
        formatter = logging.Formatter('%(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        self.log = logging.getLogger('custom')
        self.log.setLevel(logging.INFO)
        self.log.addHandler(handler)

    def start_requests(self):
        """
            This method was overrided to set the callback function.
        """
        for url in self.start_urls:
            yield Request(url, callback=self.parse_item)

    def parse_logo(self, response):
        """
            These xpath's can generate a lot of garbage output, so 
            take the first successfull xpath with a valid url.
        """
        for attr in {'@class', '@alt', '@src'}:
            for word in {'Logo', 'logo', 'Homepage', 'Home'}:
                logo_url = response.xpath(
                    LOGO_XPATH_TMPL % (attr, word)).extract_first()

                if logo_url and validators.url(logo_url):
                    return logo_url

        return ''

    def parse_item(self, response):
        """
            Parses yielded URL's from start_requests method
        """
        itemLoader = ItemLoader(item=ParsedItem(), response=response)
        itemLoader.add_value('website', response.url)
        itemLoader.add_value('phones', response.text, re=PHONE_REGEX)
        itemLoader.add_value('logo',
                             self.parse_logo(response),
                             MapCompose(lambda partial_url: urljoin(response.url, partial_url),
                                        lambda s: s.split('?')[0]))

        item = itemLoader.load_item()
        self.log.info(item)


if __name__ == '__main__':
    with sys.stdin as f:
        start_urls = set([url.strip() for url in f.readlines()])

    process = CrawlerProcess(settings=SETTINGS)
    process.crawl(CialDnbTestSpider, start_urls=start_urls)
    process.start()
