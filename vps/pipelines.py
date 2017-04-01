# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging

from urllib import parse
from sqlalchemy.ext.declarative import declarative_base

from models.vps import Provider, Plan
from workstation.libs import db


class MySQLPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        inst = cls()
        return inst

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def get_host(self, url):
        netloc = parse.urlparse(url).netloc
        """
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        """
        return netloc

    def process_item(self, crawled_item, spider):
        """Add new Plan"""
        sess = db.connect(orm='sqlalchemy')
        resp = crawled_item['resp']
        plans = crawled_item['plans']

        logging.info('crawled_item: %s', crawled_item)

        # query provider by host
        host = self.get_host(resp.url)
        provider = sess.query(Provider).filter_by(host=host).first()
        if not provider:
            # add new provider
            provider = Provider(host=host)
            sess.add(provider)
            sess.commit()

        for plan in plans:
            query = sess.query(Plan).filter_by(cores=plan['cpu'].core, 
                                               disk=plan['disk'].size, 
                                               disk_unit=plan['disk'].size_unit, 
                                               ram=plan['ram'].size, 
                                               ram_unit=plan['ram'].size_unit,
                                               provider_id=provider.id,
                                              )
            result = query.one_or_none()
            if not result:
                result = Plan(
                    provider_id=provider.id,
                    name='',

                    price=plan['price'].price,
                    period=plan['price'].period,
                    currency_code=plan['price'].currency_code,
                    currency_symb=plan['price'].currency_symb,

                    cores=plan['cpu'].core,

                    disk=plan['disk'].size,
                    disk_unit=plan['disk'].size_unit,

                    ram=plan['ram'].size,
                    ram_unit=plan['ram'].size_unit,

                    bandwidth=plan['ram'].size,
                    bandwidth_unit=plan['ram'].size_unit,

                    platform='',

                    url=resp.url,
                )

                if plan['bandwidth']:
                    result.speed=plan['bandwidth'].speed,
                    result.speed_unit=plan['bandwidth'].speed_unit,
                else:
                    result.speed = 0
                    result.speed_unit = ''

                sess.add(result)

            result.price = plan['price'].price
            result.period = plan['price'].period
            result.currency_code = plan['price'].currency_code
            result.currency_symb = plan['price'].currency_symb

        sess.commit()
        sess.close()
        return crawled_item


class Pipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        inst = cls()
        return inst

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass
