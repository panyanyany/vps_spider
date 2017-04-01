import re
import logging

from collections import OrderedDict

from helpers import text_subs_br, oneline, clean_text
from utils.src.unit_converter import Storage, Speed


logger = logging.getLogger(__name__)


def get_text(el):
    if not isinstance(el, str):
        text = oneline(el)
    else:
        text = clean_text(el)
    # text = text.lower()
    return text


class Result(object):
    # probability
    prob = 1

    def __init__(self, prob=1):
        assert isinstance(prob, (int, float))
        self.prob = prob

    def __bool__(self):
        return self.prob > 0

    def __str__(self):
        return '%s(%s)' % (self.prob > 0, self.prob)

    def __repr__(self):
        return '<Result %s>' % str(self)

    def better(self, result):
        if self.prob < result.prob:
            return result
        return self

    def all(self, *args):
        """对所有 Result 对象进行逻辑判断，类似于内嵌的 all
        原理：如果全 True，则返回 prob 最大的那个 Result
              如果有一个 False，则返回 Result(0)
        """
        if isinstance(args[0], list):
            args = args[0]
        if all(args):
            res = args[0]
            for arg in args[1:]:
                res = res.better(arg)
            return res
        return Result(0)


def plan_detect(el):
    # print(el)
    checkers = [
        Bandwidth.check(el),
        Disk.check(el).prob == 1,
        CPU.check(el),
        # Price.check(el),
    ]
    # logger.debug('detect: %s' % checkers)
    return all(checkers)


class Base(object):
    patterns = []

    def toDict(self):
        dt = {}
        for name in self.str_order:
            if hasattr(self, name):
                dt[name] = getattr(self, name)
        return dt

    def __init__(self, pattern=None, **kwargs):
        if pattern:
            self.patterns = [pattern]
        for k, v in kwargs.items():
            setattr(self, k, v)

    str_order = []
    def __str__(self):
        text = []
        if len(self.str_order) == 0:
            text.append(self.__class__.__name__)
            return repr(self)
        else:
            # text.append(self.__class__.__name__ + ':')
            for name in self.str_order:
                val = None
                if hasattr(self, name):
                    val = getattr(self, name)
                else:
                    val = name
                text.append(str(val))
        return ' '.join(text)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, str(self))
            
    def get_text(self, el):
        return get_text(el)

    def check(self, text):
        pass

    def parse(self, el):
        text = get_text(el)
        for ptn in self.patterns:
            m = ptn.search(text)
            if not m:
                continue
            for k, v in m.groupdict().items():
                if not k in dir(self):
                    raise AttributeError('%r not in %s' % (k, self.__class__))
                setattr(self, k, v)
            break
        return self


class Certain(Base):

    keys = []

    def check(self, el):
        text = self.get_text(el)
        # logger.debug(text)
        for word in self.keys:
            if isinstance(word, str):
                # it's a string
                if word in text:
                    return Result()
            else:
                # it's a pattern
                ptn = word
                if ptn.search(text):
                    return Result()
        return Result(0)


class Uncertain(Base):

    doubtless_keys = []
    keys = []

    def check(self, el):
        text = self.get_text(el)
        for word in self.doubtless_keys:
            if isinstance(word, str):
                # it's a string
                if word in text:
                    return Result(1)
            else:
                # it's a pattern
                ptn = word
                if ptn.search(text):
                    return Result(1)

        for word in self.keys:
            if isinstance(word, str):
                # it's a string
                if word in text:
                    return Result(0.5)
            else:
                # it's a pattern
                ptn = word
                if ptn.search(text):
                    return Result(0.5)
        return Result(0)


def best(detectors, el):
    scores = []
    m = 0
    idx = -1
    for i, d in enumerate(detectors):
        p = d.check(el).prob
        if p > m:
            m = p
            idx = i
        scores.append(p)

    if idx == -1:
        return []

    ret = []
    for i, s in enumerate(scores):
        if s == m:
            ret.append(detectors[i])
    return ret

class MoreThanOneBest(Exception):
    pass
