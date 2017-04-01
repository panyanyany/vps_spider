import urllib

from . import urlsolutions
from bs4 import BeautifulSoup
from libs.detectors import values


def match(url, body):
    plans = []
    for urlKey, planSetMixed in urlsolutions.mapping.items():
        if isinstance(urlKey, str):
            if urlKey != url:
                continue
            planSetArr = []
            if not isinstance(planSetMixed, list):
                planSetArr = [planSetMixed]
            else:
                planSetArr = planSetMixed
            for planSet in planSetArr:
                plans += planSet.parse(body)
            addUrl(url, body, plans)
            return plans
        else:
            # for regex
            pass
    return plans


def addUrl(url, body, plans):
    soup = BeautifulSoup(body, 'lxml')
    for p in plans:
        u = values.Url()
        u.value = url

        # title = soup.title.text.split('-')[-1].strip()
        title = urllib.parse.urlparse(url).netloc.lstrip('www.').capitalize()
        title = '.'.join(title.split('.')[:-1])
        u.title = title
        p.set(u)


"""{
    "http://www.domain.com/hosting/vps/": PlanSet("#main > div.compgrid > table > tbody > tr:nth-child({field}) > th:nth-child({plan})", PlanRange(1, 3), FieldRange(1, 9), {
        -1: CPU(0),
        1: Header,
        2: Ram,
        3: Disk,
        13: Bandwidth,
    }),
    "https://www.runabove.com/VPS-HDD.xml": PlanSet([
        ("#main > div:nth-child(7) > div > div:nth-child(7) > div:nth-child(?) > div.BlockPrice > div.monthly", PlanRange(1, 3), None, {
            0: Price,
        }),
        ("#main > div:nth-child(7) > div > div:nth-child(7) > div:nth-child(?) > ul > li:nth-child(?)", PlanRange(1, 3), FieldRange(1, 9), {
            1: Header,
            2: CPU,
            3: Disk,
            5: Bandwidth,
        })
    ]),
}"""
