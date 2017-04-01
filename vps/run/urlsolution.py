import requests
import os
import json
import sys

THIS_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.getcwd())


from utils.src.unit_converter import Storage as StorageCnvt, Speed as SpeedCnvt
from utils.src.cache import base, decorators
from utils.src.data.currency_util import findCodes, findSymb
from libs.solution import match as urlMatch
from libs.detectors import values
from libs.solution import urlsolutions

cache_dir = os.path.join(base.WebsiteFileCache.cache_dir, 'plans')
planCache = base.WebsiteFileCache(cache_dir=cache_dir, file_mode='b')


@decorators.Memorize(decorators.PositionSelector(0), planCache)
def Get(url, headers):
    print('request:', url)
    resp = requests.get(url, headers=headers)
    return resp

@decorators.Memorize(decorators.PositionSelector(0), planCache)
def GetCurrencyRate(url):
    resp = requests.get(url)
    return resp.json()

def crawl(url):
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        # 'Referer': 'https://www.stablehost.com/vps-hosting.php',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'en-US;q=0.6,en;q=0.4',
        # 'Upgrade-Insecure-Requests':'1',
    }
    resp = Get(url, headers=headers)
    # print(resp)
    plans = urlMatch(url, resp.text)
    return plans


def dealDisk(plans):
    for p in plans:
        disk = p.disk
        if disk.size_unit == 'GB': continue
        disk.size = StorageCnvt.convert(float(disk.size), disk.size_unit, 'GB')
        disk.size_unit = 'GB'
        disk.size *= int(disk.disk_cnt)
        disk.disk_cnt = 1

def dealRAM(plans):
    for p in plans:
        disk = p.ram
        if disk.size_unit.upper() == 'MB': continue
        disk.size = StorageCnvt.convert(float(disk.size), disk.size_unit, 'MB')
        disk.size_unit = 'MB'


def dealCurrency(plans):
    EUR_based = GetCurrencyRate('http://api.fixer.io/latest')
    USD_based = {}
    USD_rate = EUR_based['rates']['USD']
    for code, value in EUR_based['rates'].items():
        if code == 'USD':
            continue
        USD_based[code] = float(value) / float(USD_rate)
    USD_based['EUR'] = 1 / float(USD_rate)

    for p in plans:
        price = p.price
        symb = price.currency_symb
        code = price.currency_code

        price.price = float(price.price) / int(price.period)
        price.period = 1

        if symb == '$' and code == 'USD':
            price.price = '%.2f' % price.price
            continue
        _symb = findSymb(code.upper())
        if symb not in _symb:
            raise Exception('currency_symb unmatched:(%s != %s) %s' % (symb, _symb, p.url))
        price.price = float(price.price) / USD_based[code]
        price.price = '%.2f' % price.price
        price.currency_symb = '$'
        price.currency_code = 'USD'

def dealTraffic(plans):
    for p in plans:
        if not hasattr(p, 'traffic') or p.traffic is None:
            continue
        tr = p.traffic
        if isinstance(tr.volume, str) and ',' in tr.volume:
            tr.volume = tr.volume.replace(',', '')

        tr.volume = float(tr.volume)
        if tr.volume_unit != 'MB':
            tr.volume = StorageCnvt.convert(tr.volume, tr.volume_unit, 'MB')

def dealNetworkOut(plans):
    for p in plans:
        if not hasattr(p, 'networkout') or p.networkout is None:
            continue
        tr = p.networkout
        tr.speed = float(tr.speed)
        if tr.speed_unit.lower() != 'mbps':
            tr.speed = SpeedCnvt.convert(tr.speed, tr.speed_unit, 'mbps')


def dealCPU(plans):
    for p in plans:
        if p.cpu is None:
            cpu = values.CPU()
            cpu.core = 1
            p.set(cpu)
        elif p.cpu.core == 0:
            p.cpu.core = 1


def save(plans):
    dt = [p.toDict() for p in plans]
    with open('data/plans.json', 'w+') as fp:
        json.dump(dt, fp)

def printPlans(plans):
    # arr = [str(p.toDict()) for p in plans]
    arr = [str(p) for p in plans]
    print('\n\n'.join(arr))

plans = crawl('https://www.alpharacks.com/')
dealCurrency(plans)
printPlans(plans)

# exit(0)

# [ crawl(url) for url in urlsolutions.mapping ]
plans = []
for url in urlsolutions.mapping:
    _plans = crawl(url)
    plans += _plans

dealCurrency(plans)
dealDisk(plans)
dealRAM(plans)
dealTraffic(plans)
dealNetworkOut(plans)
dealCPU(plans)
save(plans)
