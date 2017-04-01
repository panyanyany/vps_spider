import re

from helpers import text_subs_br, get_text, oneline, clean_text

class Base(object):
    class meta: pass
    patterns = []

    def __getattr__(self, name):
        if name in self.meta.__dict__:
            return getattr(self.meta, name)
        return super().__getattr__(name)

    def __setattr__(self, name, value):
        if name in self.meta.__dict__:
            setattr(self.meta, name, value)
        else:
            super().__setattr__(name, value)

    def __init__(self, pattern=None, **kwargs):
        if pattern:
            self.patterns = [pattern]
        for k, v in kwargs.items():
            setattr(self, k, v)

    def parse(self, el):
        text = oneline(el)
        for ptn in self.patterns:
            m = ptn.search(text)
            if not m:
                continue
            gd = m.groupdict()
            for field, value in gd.items():
                setattr(self, field, value)
            break


class CPU(Base):
    class meta:
        brand = ''
        cores = 0.0
        cpu_type = CPU # vCPU
        freq = 0.0
        freq_unit = 'GHz'

    patterns = [
        re.compile("(?P<cores>\d+.?\d+) (?P<cpu_type>vCPU|CPU)", re.I),
        re.compile("(?P<cores>\d+.?\d+)", re.I),
    ]


class Storage(Base):
    class meta:
        size = 0
        size_unit = 'MB'

    patterns = [
        re.compile("(\d+.?\d*) *(mb|gb|tb)", re.I),
    ]
