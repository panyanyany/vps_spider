import re
import logging
import types

from collections import OrderedDict

from helpers import text_subs_br, get_text, oneline, clean_text
from utils.src.unit_converter import Storage as StorageCnvt, Speed as SpeedCnvt
from libs.detectors import headers
from libs.detectors.base import Uncertain, Result, best, Base
from utils.src.re import ssub
from utils.src.data import currency


logger = logging.getLogger(__name__)


def value_detect(el, detectors=None):
    detectors = detectors or [
        Price,
    ]
    values = best(detectors, el)
    if len(values) > 1:
        # 一个 el 居然匹配到多个 value, 说明 value 的匹配算法有问题，需要修改代码了!
        raise Exception("got %d value on %r, they are %s" % (len(values), oneline(el), values))
    if len(values) == 1:
        return values[0]
    return None



class Name(Uncertain):
    name = ''
    str_order = ['name']

    def check(self, el):
        """只要被 headers.Name 检查通过了，此处就不需要再检查"""
        return Result()

    def parse(self, el):
        self.name = oneline(el).strip()
        return self

class _Bandwidth(Uncertain):

    absolute_keys = ['gbps', 'mbps', 'gbit']
    keys = ['gb', 'tb']

    str_order = ['volume', 'volume_unit', '@', 'speed', 'speed_unit']

    volume = 0
    volume_unit = 'MB'

    speed = 0
    speed_unit = 'mbps'

    volume_ptn = re.compile("(\d+.?\d*) *(gb|mb|tb)", re.I)
    speed_ptn = re.compile("(\d+.?\d*) *(gbps|mbps)", re.I)

    def check(self, el):
        res = super().check(el)
        if not res:
            return res

        try:
            self.parse(el)
        except Exception as e:
            return Result(0)
        return res 

    def parse(self, el):
        text = oneline(el)

        m = self.speed_ptn.search(text)
        if not m:
            logger.warn("speed_ptn search failed from %r" % text)
        else:
            val, unit = m.groups()
            self.speed = SpeedCnvt.convert(float(val), unit, self.speed_unit)
            text = ssub(m.span(), text)

        m = self.volume_ptn.search(text)
        if m:
            val, unit = m.groups()
            self.volume = StorageCnvt.convert(float(val), unit, self.volume_unit)
        else:
            raise Exception("volume_ptn search failed from %r" % text)

        return self


class Traffic(Uncertain):
    # absolute_keys = ['gbps', 'mbps', 'gbit']
    keys = ['gb', 'tb']

    str_order = ['volume', 'volume_unit']

    volume = 0
    volume_unit = 'MB'

    volume_ptn = re.compile("(\d+.?\d*) *(gb|mb|tb)(?!\w)", re.I)

    def check(self, el):
        res = super().check(el)
        if not res:
            return res

        try:
            self.parse(el)
        except Exception as e:
            return Result(0)
        return res 

    def parse(self, el):
        text = oneline(el)

        m = self.volume_ptn.search(text)
        if m:
            val, unit = m.groups()
            self.volume = StorageCnvt.convert(float(val), unit, self.volume_unit)
        else:
            raise Exception("volume_ptn search failed from %r" % text)

        return self


class NetworkOut(Uncertain):
    """ 服务器向公网传输的速度，即用户的下载速度, 等同于 uplink, port speed
    @see http://www.webhostingtalk.com/showthread.php?t=975035
    """
    absolute_keys = ['gbps', 'mbps', 'gbit', 'gigabit']

    str_order = ['@', 'speed', 'speed_unit']

    speed = 0.0
    speed_unit = 'mbps'

    speed_ptn = re.compile("(\d+.?\d*) *(gbps|mbps|gigabit|gbit)", re.I)

    def check(self, el):
        res = super().check(el)
        if not res:
            return res

        try:
            self.parse(el)
        except Exception as e:
            return Result(0)
        return res 

    def parse(self, el):
        text = oneline(el)

        m = self.speed_ptn.search(text)
        if not m:
            logger.warn("speed_ptn search failed from %r" % text)
        else:
            val, unit = m.groups()
            unit = unit.lower()
            if unit in ('gbit', 'gigabit'):
                unit = 'gbps'
            self.speed = SpeedCnvt.convert(float(val), unit, self.speed_unit)
            text = ssub(m.span(), text)

        return self


class NetworkIn(NetworkOut): pass


class Storage(Uncertain):

    size = 0
    size_unit = 'MB'
    storage_ptn = re.compile("(\d+.?\d*) *(mb|gb|tb)", re.I)

    keys = [
        re.compile("(?P<size>\d+\.?\d*) *(?P<size_unit>mb|gb|tb)", re.I),
        re.compile("(?P<disk_num>\d+) *x *(?P<size>\d+) *(?P<size_unit>mb|gb|tb)", re.I),
    ]

    def parse(self, el):
        text = self.get_text(el)

        for ptn in self.keys:
            m = ptn.search(text)
            if not m:
                continue
            gd = m.groupdict()
            unit = gd['size_unit']
            size = float(gd['size'])
            if 'disk_num' in gd:
                size *= int(gd['disk_num'])
            self.size = StorageCnvt.convert(size, unit, self.size_unit)
            return self

        raise Exception("storage_ptn search fail on %r" % text)


class Disk(Storage):
    str_order = ['disk_cnt', 'x', 'size', 'size_unit', 'disk_type']

    disk_cnt = 1
    disk_type = 'HDD'
    ssd_ptn = re.compile("(ssd|solid)", re.I)
    sas_ptn = re.compile("(sas)", re.I)

    def parse(self, el):
        self = super().parse(el)

        text = oneline(el)

        if self.ssd_ptn.search(text):
            self.disk_type = 'SSD'
        elif self.sas_ptn.search(text):
            self.disk_type = 'SAS'

        return self


class RAM(Storage):

    str_order = ['size', 'size_unit']


class VSwap(Storage):

    str_order = ['size', 'size_unit']


class CPU(Uncertain):

    str_order = ['cpu_cnt', 'x', 'manuf', 'core', 'cores', 'cpu_type', 'freq', 'freq_unit']
    keys = [re.compile("(\d+)")]

    core = 0
    core_ptn = re.compile("(\d+)")
    manuf = ''        
    family = ''
    cpu_cnt = 1
    cpu_type = 'CPU' # vCPU
    freq = 0.0
    freq_unit = 'GHz'

    def parse(self, el):
        text = oneline(el)

        m = self.core_ptn.search(text)
        if not m:
            raise Exception("core_ptn search failed on %r" % text)
        val = m.groups()[0]
        self.core = float(val)
        return self

class Price(Uncertain):

    doubtless_keys = [
        # $ 3 .49 /month
        re.compile(r'(?P<symbol>[^\s\w\d.]) (?P<price>\d+ .\d+) / ?(?P<period_unit>mo|ye|yr|qtr)', re.I),

        # €30.00/mo
        # $3.99/mo.
        # $ 9.99 /MONTH
        # €6,50/month

        # Starting from $11.99 USD \nMonthly
        # Starting from $15\nper month
        # Starting from \n£2.50GBP \nAnnually
        # $4.48 USD Annually 
        # Starting at $ 5.00 monthly  
        # re.compile(r'([^\s\w\d]?) *(\d+[.,]*\d*) *(\w*) */*(\w*)', re.I),
        re.compile(r'(?P<symbol>[^\s\w\d]?) ?(?P<price>\d+[.,]*\d*) per (?P<period_unit>month|year)', re.I),

        re.compile(r'(?P<symbol>[^\s\w\d]?) ?(?P<price>\d+[.,]*\d*) */ *(?P<period_unit>mo|ye|yr|qtr)', re.I),
        re.compile(r'(?P<symbol>[^\s\w\d]?) ?(?P<price>\d+[.,]*\d*) */ *(?P<period>\d+) (?P<period_unit>mo|ye|yr|qtr)', re.I),
        re.compile(r'(?P<symbol>[^\s\w\d]?) ?(?P<price>\d+[.,]*\d*) *(?P<currency_code>\w*) (?P<period_unit>monthly|annually)', re.I),
        re.compile(r'(?P<symbol>[^\s\w\d]) ?(?P<price>\d+[.,]*\d*) *(?P<currency_code>\w*)', re.I),
    ]
    price = 0.0
    currency_symb = '$'
    currency_code = 'USD'
    period = 1
    period_unit = 'mo'

    str_order = ['currency_symb', 'price', 'currency_code', '/', 'period', 'period_unit']

    def parse(self, el):
        text = oneline(el)
        m = None
        for ptn in self.doubtless_keys:
            m = ptn.search(text)
            if m:
                break
        if not m:
            raise Exception("price pattern search failed on %r" % text)

        gd = m.groupdict()
        symbol = gd['symbol']
        price = gd['price']
        currency_code = gd.get('currency_code')
        period = gd.get('period')
        period_unit = gd.get('period_unit')

        if ',' in price:
            price = price.replace(',', '.')
        price = price.replace(' ', '')
        self.price = float(price)
        if symbol:
            if symbol not in currency.symbols:
                raise Exception("unexpected currency symbol(=%r)(utf8=%r) on %r" % (symbol, symbol.encode('utf8'), text))
            self.currency_symb = symbol
        if currency_code:
            if currency_code not in currency.codes:
                raise Exception("unexpected currency code(=%r)(utf8=%r) on %r" % (currency_code, currency_code.encode('utf8'), text))
            self.currency_code = currency_code
        if period_unit:
            prefix = period_unit[:2].lower()
            if prefix in ('mo'):
                pass
            elif prefix in ('yr', 'ye', 'an'):
                self.period *= 12
                # self.period_unit = 'yr'
            elif prefix in ('qtr'):
                self.period *= 4
            else:
                raise Exception("unexpected period(=%r) on %r" % (period_unit, text))
        if period:
            self.period = int(period)
        return self

    def check(self, el):
        try:
            self.parse(el)
            return Result(1)
        except:
            return Result(0)


class DDoS(Base): 
    str_order = ['available', 'desc']
    available = False
    desc = ''


class Snapshot(Base):
    str_order = ['num', 'status']
    num = 0
    status = ''


class Panel(Base):
    str_order = ['name']
    name = ''


class IP(Base):
    str_order = ['ipv4', 'IP', 'relation', 'ipv6', '/', 'ipv6_fp', 'IPv6']
    patterns = [
        re.compile('(?<!\w)(?P<ipv4>\d+)'),
    ]

    ipv4 = 0
    ipv6 = 0
    # FP, Format Prefix
    ipv6_fp = 0

    relation = 'or'


class Virt(Base):
    str_order = ['vtype']
    vtype = ''


class Location(Base):
    str_order = ['loc']
    loc = []


class Backup(Base):
    str_order = ['enabled']
    enabled = ''


class Trial(Base):
    str_order = ['days', 'day', 'Trial']
    days = 0


class Url(Base):
    str_order = ['title', 'value']
    title = ''
    value = ''
