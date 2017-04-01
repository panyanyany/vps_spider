import re
import logging

from helpers import text_subs_br, get_text, oneline
from libs.detectors.base import Result, Uncertain, MoreThanOneBest, best


logger = logging.getLogger(__name__)


class Base(Uncertain):
    with_value = False
    class_keys = []

    def check(self, el):
        result = super().check(el)
        if self.class_keys:
            class_result = self.check_class(el)
            result = result.better(class_result)
        return result
            

    def check_class(self, el):
        result, _ = self._select(el)
        return result

    def select(self, el):
        result, found_el = self._select(el)
        return found_el

    def _select(self, el):
        if hasattr(el, 'text'):
            # 先检查 class 的值，再检查 id 的值
            attrs = ['class', 'id']
            for attr in attrs:
                # 先检查节点本身的属性
                el_class = el.get(attr) or []
                el_class = ' '.join(el_class).lower()
                # logger.debug("get %r attr: %r", attr, el_class)
                maybe = sum([opt[1] for opt in self.class_keys if opt[0] in el_class])
                if maybe > 0:
                    return Result(maybe), el

                # 检查子节点的属性
                for opt in self.class_keys:
                    els = el.select('[%s*=%s]' % (attr, opt[0]))
                    if els:
                        return Result(opt[1]), els[0]
        return Result(0), None


def header_detect(el, detectors=None):
    detectors = detectors or [
        Bandwidth,
        CPU,
        VSwap,
        Disk,
        RAM,
        Price,
        Name,
    ]
    headers = best(detectors, el)
    if len(headers) > 1:
        # 一个 el 居然匹配到多个 header, 说明 header 的匹配算法有问题，需要修改代码了!
        raise MoreThanOneBest("got %d header on %r, they are %s" % (len(headers), oneline(el), headers))
    if len(headers) == 1:
        return headers[0]
    return None


def headers_match(els):
    cls = [
        Bandwidth,
        CPU,
        VSwap,
        Disk,
        RAM,
        Price,
        Name,
    ]
    fields = []
    for el in els:
        spec = header_detect(el, cls)
        if not spec:
            # 在此情境下，不能匹配的 el 应该占到多数，所以用 debug 
            logger.debug("no match Header for %r" % oneline(el))
        else:
            cls.remove(spec)
        fields.append(spec)
    return fields


class Name(Base):
    name = ''
    str_order = ['name']
    class_keys = [
        ('name', 0.7), 
        ('Name', 0.7), 
        ('NAME', 0.7), 

        ('title', 0.7), 
        ('Title', 0.7), 
        ('TITLE', 0.7), 

        ('head', 0.7),
        ('Head', 0.7),
        ('HEAD', 0.7),
    ]


    def parse(self, el):
        self.name = oneline(el).strip()
        return self


class Bandwidth(Base):

    doubtless_keys = ['bandwidth', 'traffic', 'transfer']


class Disk(Base):

    doubtless_keys = [
        'hdd', 
        'sas', 
        'ssd', 
        'storage', 
        'hard drive', 
        'dedicated disk space',
        'disk', 
        re.compile(r'solid +state +drive', re.I),
        re.compile(r'\(*raid *\d+\)*', re.I), 
    ]


class RAM(Base):

    doubtless_keys = [
        'memory',
        'ram',
        'dedicated ram',
    ]


class VSwap(Base):
    doubtless_keys = ['vswap']


class CPU(Base):

    doubtless_keys = ['cpu', 'core']


class Price(Base):

    doubtless_keys = [
        'price', 
        re.compile(r'starting (at|from)', re.I),
        re.compile(r'period', re.I),
    ]

    class_keys = [
        ('price', 1),
        ('Price', 1),
        ('PRICE', 1),
    ]
