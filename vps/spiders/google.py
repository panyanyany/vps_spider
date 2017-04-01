# -*- coding: utf-8 -*-
import scrapy
import logging
import os
import urllib
import json

import settings
from libs.plan_parser import PlanParser
from items import VpsItem
from workstation.libs import cache

# defined in https://console.developers.google.com/apis/credentials?project=goagent-1114
google_api_key = ''
# custom search engine id
# defined in https://cse.google.com/cse/all
google_cse_id = ''
query='vps'
search_url = "https://www.googleapis.com/customsearch/v1"
search_args = dict(q=query, cx=google_cse_id, key=google_api_key)

logger = logging.getLogger(__name__)
# logger = logging

class GoogleSpider(scrapy.Spider):
    name = "google"
    allowed_domains = []
    visited_urls = {}
    # stats key
    sk_add_provider_urls = 'google/add_provider_urls'

    def __init__(self, page_tot='10', proxy_enable='0', *args, **kwargs):
        super(GoogleSpider, self).__init__(*args, **kwargs)

        if page_tot.isdigit():
            self.page_tot = int(page_tot)
        else:
            self.page_tot = 10

        if proxy_enable.isdigit():
            self.proxy_enable = bool(int(proxy_enable))
        else:
            self.proxy_enable = False
        logger.info('GoogleSpider initial settings: page_tot=%s, proxy_enable=%s', self.page_tot, self.proxy_enable)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(GoogleSpider, cls).from_crawler(crawler, *args, **kwargs)
        spider.crawler.stats.set_value(cls.sk_add_provider_urls, 0)
        return spider

    def set_vps_providers_urls(self, url):
        r = cache.connect()
        urls = r.lrange(cache.keys.vps_providers_urls, 0, -1)
        urls = list(map(lambda e: e.decode('utf8'), urls))
        if url not in urls:
            logger.info('push url:%s', url)
            self.crawler.stats.inc_value(self.sk_add_provider_urls)
            r.lpush(cache.keys.vps_providers_urls, url)

    def start_requests(self):
        num = 10
        urls = []
        for i in range(0, self.page_tot):
            start = i * num + 1
            search_args['start'] = start
            url = "{}?{}".format(search_url, urllib.parse.urlencode(search_args))
            urls.append(url)

        for url in urls:
            meta = {}
            # proxy of lantern
            if self.proxy_enable:
                meta.update({'proxy': 'http://127.0.0.1:49758'})
            # proxy of shadowsocks
            # meta = {'proxy': 'socks5://127.0.0.1:1080'}
            # meta = {}
            yield scrapy.Request(url=url, callback=self.parse, meta=meta)

    def parse(self, response):
        data = json.loads(response.body.decode('utf8'))
        for item in data['items']:
            link = item['link']
            self.set_vps_providers_urls(link)
