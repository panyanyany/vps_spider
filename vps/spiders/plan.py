# -*- coding: utf-8 -*-
import scrapy
import logging
import os
import urllib
import pickle

import settings

from libs.plan_parser import PlanParser
from libs.solution import match as solutionMatch
from libs.solution import urlsolutions
from items import VpsItem
from workstation.libs import cache
from utils.src.cache import base, decorators, flag


cache_dir = os.path.join(base.WebsiteFileCache.cache_dir, 'plans')
planCache = base.WebsiteFileCache(cache_dir=cache_dir, file_mode='b')
logger = logging.getLogger('plan')
flagOfGAUU = flag.Base("GB_attr_unaware_urls")


class PlanSpider(scrapy.Spider):
    name = "plan"
    allowed_domains = []
    visited_urls = {}

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(PlanSpider, cls).from_crawler(crawler, *args, **kwargs)
        spider.stats = crawler.stats
        return spider

    def getUrls(self):
        return urlsolutions.mapping.keys()

    def start_requests(self):
        # urls = self.get_vps_providers_urls()
        # logging.info('got %d urls: %r', len(urls), urls)
        for url in self.getUrls():
            # meta = {'proxy': 'http://127.0.0.1:8888'}
            meta = {}
            yield scrapy.Request(url=url, callback=self.parse, meta=meta)

    def parse(self, response):
        plans = solutionMatch(response.url, response.text)
        if plans:
            yield plans

    def close_spider(self):
        # urls = self.stats.get_value('spider/failed_GB_pages')
        # self.stats.set_value('spider/failed_GB_pages', ','.join(urls))
        pass
