import re
import types


from bs4 import BeautifulSoup
from ..detectors.kit import Plan
from ..detectors.base import get_text, Base
from utils.src.inspect_util import is_class


class SingleSelector:
    def __init__(self, css_selector):
        self.css_selector = css_selector

    def apply(self, soup):
        # to compatile with bs4
        css_outer = self.css_selector.replace('nth-child', 'nth-of-type')
        domList = soup.select(css_outer)
        return domList


class BinarySelector:
    """use css selector to select out an array of plans which as well as an array containing fields"""
    def __init__(self, css_outer, css_inner, planDivided=False, planRange=tuple()):
        self.css_outer = css_outer
        self.css_inner = css_inner
        self.planDivided = planDivided
        self.planRange = planRange

    def innerOut(self, rows):
        """if plan's fields were divided into several nodes
        use this method to make them into one 
        """
        plans = [[] for i in range(len(rows[0]))]
        for a in rows:
            for i, e in enumerate(a):
                plans[i].append(e)
        return plans

    def apply(self, soup):
        """apply css selector to html dom"""
        # to compatile with bs4
        css_outer = self.css_outer.replace('nth-child', 'nth-of-type')
        outers = soup.select(css_outer)
        # print()
        # print(repr(css_outer), len(outers))
        plans = []
        for outer in outers:
            # to compatile with bs4
            css_inner = self.css_inner.replace('nth-child', 'nth-of-type')
            inners = outer.select(css_inner)
            # print(repr(css_inner), len(inners), outer, '\n')
            if len(inners) == 0:
                continue
            plans.append(inners)

        if self.planDivided:
            plans = self.innerOut(plans)

        s, e = 0, len(plans)
        if len(self.planRange) == 1:
            s = self.planRange[0]
        elif len(self.planRange) == 2:
            s, e = self.planRange

        return plans[s:e]


class PlanSet(object):
    def __init__(self, *args):
        if len(args) != 1:
            args = [args]
        else:
            args = args[0]
        self.selectorArr = args

    def parse(self, body):
        soup = BeautifulSoup(body, 'lxml')
        plans = []
        singleSelectors = []
        binarySelectors = []

        # get different-style data from multiple selector templates respectly
        # print()
        for selector_set in self.selectorArr:
            binary_select_args, valueMapping = selector_set
            if len(binary_select_args) == 1:
                singleSelectors.append(selector_set)
            else:
                binarySelectors.append(selector_set)


        for binary_select_args, valueMapping in binarySelectors:
            ds = BinarySelector(*binary_select_args)
            domPlans = ds.apply(soup)

            # print(repr(binary_select_args), domPlans)
            for planIndex, domPlan in enumerate(domPlans):
                if len(plans) == planIndex:
                    plans.append(Plan())
                plan = plans[planIndex]
                self.mapValues(plan, domPlan, valueMapping)
            # print('-- dom select done\n')

        for singleSelector, valueMapping in singleSelectors:
            ss = SingleSelector(*singleSelector)
            domList = ss.apply(soup)

            for plan in plans:
                self.mapValues(plan, domList, valueMapping)

        return plans


    def mapValues(self, plan, domList, valueMapping):
        for fieldIndex, mappedValues in valueMapping.items():
            domField = domList[fieldIndex]
            fillers = mappedValues
            if not isinstance(fillers, (tuple, list)):
                fillers = [fillers]
            for filler in fillers:
                self.setField(plan, filler, domField)


    def setField(self, plan, filler, el):
        # 兼容旧版
        if is_class(filler):
            filler = ValueSearch(filler)

        cls = filler.val_cls
        field = plan.exists(cls())
        if not field:
            field = cls()

        filler.parse(field, el)
        plan.set(field)


class DomRange(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end


class PlanRange(DomRange): pass
class FieldRange(DomRange): pass


class ValueMatch:
    def __init__(self, val_cls, str_or_re):
        if isinstance(str_or_re, str):
            str_or_re = re.compile(str_or_re, re.I)
        self.target = str_or_re
        self.val_cls = val_cls

    def search(self, el):
        text = get_text(el)
        if isinstance(self.target, dict):
            for k, vals in self.target.items():
                default = None
                if len(vals) == 1:
                    ptn = vals[0]
                else:
                    ptn, default = vals
                m = ptn.search(text)
                if not m:
                    if default is None:
                        raise Exception("pattern(%s) search failed on %r" % (ptn, text))
                    v = default
                else:
                    v = m.groupdict()[k]
                yield k, v
        else:
            m = self.target.search(text)
            if not m:
                raise Exception("pattern(%s) search failed on %r" % (self.target, text))
            gd = m.groupdict()
            for k, v in gd.items():
                yield k, v


    def parse(self, value_inst, el):
        for k, v in self.search(el):
            if k in dir(value_inst):
                if v is None:
                    continue
                setattr(value_inst, k, v)
            else:
                raise Exception("%r not in value of %s" % (k, value_inst.__class__))
        return


class ValueAppend(ValueMatch):
    def search(self, text):
        text = get_text(el)
        i = 0
        pos = 0
        while 1:
            m = self.target.search(text, pos)
            if not m:
                if i == 0:
                    raise Exception("pattern(%s) search failed on %r" % (self.target, text))
                else:
                    break
            gd = m.groupdict()
            for k, v in gd.items():
                yield k, v
            i+=1
            pos = m.span()[1]
        return

    def parse(self, value_inst, el):
        exist = {}
        for k, v in self.search(el):
            if k in dir(value_inst):
                values = getattr(value_inst, k)
                values.append(v)
                setattr(value_inst, k, values)
            else:
                raise Exception("%r not in value of %s" % (k, value_inst.__class__))
        return


class ValueSearch:
    def __init__(self, cls):
        self.val_cls = cls

    def parse(self, value_inst, el):
        value_inst.parse(el)


class ValueSet:
    def __init__(self, cls, **fields):
        self.val_cls = cls
        self.fields = fields

    def parse(self, value_inst, el=None):
        for k, v in self.fields.items():
            setattr(value_inst, k, v)


class ValuePipe:
    def __init__(self, cls, preps, match=None):
        self.val_cls = cls
        if not isinstance(preps, list):
            preps = [preps]
        self.preps = preps
        self.match = match

    def parse(self, value_inst, el):
        text = get_text(el)
        for prep in self.preps:
            if isinstance(prep, types.LambdaType):
                text = prep(text)
            else:
                text = prep.process(text)
        if self.match:
            self.match.parse(value_inst, text)
        else:
            value_inst.parse(text)
        return 


class Prep:
    def process(self, el):
        return el


class ExtractPrep(Prep):
    def __init__(self, src, dst):
        if isinstance(src, str):
            src = re.compile(src)
        self.src = src
        self.dst = dst

    def process(self, text):
        m = self.src.search(text)
        if not m:
            raise Exception('search failed! ptn:%r, text:%r' % (self.src, text))
        gd = m.groupdict()
        if gd:
            new_text = self.dst.format(**gd)
        else:
            new_text = self.dst.format(*m.groups())
        return new_text
