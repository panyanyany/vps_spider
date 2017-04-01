# -*- coding: utf-8 -*-
import scrapy
import logging
import os
import urllib
import pickle

import settings

from libs.plan_parser import PlanParser
from libs.solution import match as solutionMatch
from items import VpsItem
from workstation.libs import cache
from utils.src.cache import base, decorators, flag


from scrapy.utils.trackref import object_ref
class BroadSpider(object_ref):
    def generate_spiders(cls):
        pass

cache_dir = os.path.join(base.WebsiteFileCache.cache_dir, 'plans')
planCache = base.WebsiteFileCache(cache_dir=cache_dir, file_mode='b')
logger = logging.getLogger('plan')
flagOfGAUU = flag.Base("GB_attr_unaware_urls")


class ExtraInfoSpider(scrapy.Spider):
    name = "extra_info"
    allowed_domains = []
    visited_urls = {}

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ExtraInfoSpider, cls).from_crawler(crawler, *args, **kwargs)
        spider.stats = crawler.stats
        return spider

    """
    def save_to_file(self, step_name, resp, pp):
        root = 'logs'
        title = resp.css('title')[0].xpath('text()').extract()[0]
        netloc = urllib.parse.urlparse(resp.url).netloc
        name = ''.join([c for c in title if c.isalnum() or c.isspace()])[:30]
        name = netloc + '-' + name.replace(' ', '_')
        dir_path = os.path.join(root, step_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        file_path = os.path.join(dir_path, name) + '.htm'
        with open(file_path, 'w') as fp:
            fp.write(str(pp.soup))
    """

    def getUrls(self):
        return [
            'https://billing.virmach.com/cart.php?a=confproduct&i=0',
        ]

    def start_requests(self):
        # urls = self.get_vps_providers_urls()
        # urls = self.get_vps_providers_urls()
        # logging.info('got %d urls: %r', len(urls), urls)
        for url in self.getUrls():
            # meta = {'proxy': 'http://127.0.0.1:8888'}
            meta = {}
            yield scrapy.Request(url=url, callback=self.parse, meta=meta)

    def parse(self, response):
        item = {}
        if response.url == 'https://billing.virmach.com/cart.php?a=confproduct&i=0':
            el = response.css('#main-body > div.row > div > form > fieldset:nth-child(9) > div:nth-child(2) > div.col-md-4')
            logger.debug(el)
        yield item

    def close_spider(self):
        # urls = self.stats.get_value('spider/failed_GB_pages')
        # self.stats.set_value('spider/failed_GB_pages', ','.join(urls))
        pass

