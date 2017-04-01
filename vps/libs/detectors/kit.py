from collections import OrderedDict

from helpers import oneline
from libs.detectors.base import Result, best
from libs.detectors import headers
from libs.detectors import values


def plan_detect(el):
    # print(el)
    checkers = [
        # headers.Bandwidth.check(el),
        headers.Disk().check(el),
        headers.CPU().check(el),
        # Price.check(el),
    ]
    # logger.debug('detect: %s' % checkers)
    return all(checkers)


class Plan(object):

    def toDict(self):
        dt = {}
        for field, value in self.fields.items():
            if value is None:
                continue
            dt[field] = value.toDict()
        return dt

    def __getitem__(self, key):
        return self.fields[key]

    def __init__(self):
        self.fields = OrderedDict([
            ('name', None),
            ('price', None),
            ('disk', None),
            ('ram', None),
            ('cpu', None),
            # ('vswap', None),
            # ('bandwidth', None),
            ('traffic', None),
            ('networkout', None),
            ('ip', None),
            ('location', None),
        ])

    def exists(self, obj):
        name = obj.__class__.__name__.lower()
        if name in self.fields:
            return self.fields[name]
        return False
    
    def set(self, spec):
        name = spec.__class__.__name__.lower()
        val = spec
        setattr(self, name, val)

        old = self.fields.get(name)
        self.fields[name] = val
        return old

    def toJson(self):
        ret = OrderedDict()
        for name, spec in self.fields.items():
            ret[name] = str(spec)
        return ret

    def __str__(self):
        # print_order = 'name', 'cpu', 'disk', 'ram', 'vswap', 'bandwidth', 'price'
        ary = []
        for name, spec in self.fields.items():
            ary.append('%s: %s' % (name, spec))
        return '\n'.join(ary)

    __repr__ = __str__


class Shell(object):
    def __init__(self, detectors, real_check):
        self.detectors = detectors
        self.real_check = real_check

    def __str__(self):
        return '%s' % self.detectors[0].__name__

    def __repr__(self):
        return '<%s>' % str(self)

    def check(self, el):
        results = []
        for d in self.detectors:
            results.append(d().check(el))
        return self.real_check(results)


def spec_detect(el, detectors=None):
    detectors = detectors or [
        Shell([headers.Bandwidth, values.Bandwidth], lambda results: results[0].better(results[1])),
        Shell([headers.CPU], lambda results: results[0]),
        Shell([headers.VSwap], lambda results: results[0]),
        Shell([headers.Disk, values.Disk], lambda results: Result.all(results)),
        Shell([headers.RAM, values.RAM], lambda results: Result.all(results)),
        # Shell([headers.RAM], lambda results: results[0]),
        Shell([headers.Price, values.Price], lambda results: results[0].better(results[1])),
        Shell([headers.Name, ], lambda results: results[0]),
    ]

    res = best(detectors, el)
    if len(res) == 0:
        # logger.warn('no matched SpecDetector for %r' % el)
        return None

    if len(res) != 1:
        # logger.error("expect 1 detector, got %d, they are: %r, when detecting: %r" % (len(res), res, el))
        raise Exception("expect 1 detector, got %d, they are: %r, when detecting: %r" % (len(res), res, oneline(el)))

    name = res[0].detectors[0].__name__
    value_detector = getattr(values, name)
    return value_detector.parse(el)


def get_value_class(header_cls):
    return getattr(values, header_cls.__name__)
