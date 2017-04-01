import scrapy
import os
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import inside_project, get_project_settings
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner


THIS_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(THIS_DIR, '..'))

sys.path.insert(0, os.path.join(THIS_DIR, '../..'))
import vps

import spiders.plan


# process = CrawlerProcess(get_project_settings())
# 
broadSpiderCls = spiders.plan.PlanBroadSpider
allSpiderCls = broadSpiderCls().generate_spiders()
# for spidercls in allSpiderCls:
#     process.crawl(spidercls)
# 
# process.start() # the script will block here until all crawling jobs are finished

runner = CrawlerRunner(get_project_settings())

@defer.inlineCallbacks
def crawl(clses):
    for cls in clses:
        yield runner.crawl(cls)
    reactor.stop()

crawl(allSpiderCls)
reactor.run() # the script will block here until the last crawl call is finished
