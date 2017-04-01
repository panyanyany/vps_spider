import re
import logging

from collections import OrderedDict
from bs4 import BeautifulSoup

from helpers import text_with_space, get_text, impact_els, oneline
from libs.detectors import values as ValueDetectors
from libs.detectors import headers as HeaderDetectors
from libs.detectors.headers import header_detect, headers_match
from libs.detectors.values import value_detect
from libs.detectors.kit import plan_detect, Plan, spec_detect, get_value_class
from libs.detectors.base import Result, Uncertain, MoreThanOneBest
from utils.src.debug_kit import terracing


logger = logging.getLogger(__name__)


def check_specs(el):
    """检查该节点除了 GB 外是否还有其他 specs 信息"""
    # got GB node, check if contains more than GB info
    counts = 0
    for e in el.children:
        text = get_text(e).lower()
        if 'gb' in text or 'mb' in text:
            counts += 1
    contain_specs = counts > 1
    return contain_specs


class PlanParser(object):
    search_ptn_attr_name_tpl = 'search_%s'
    search_ptn_attr_name_2nd_tpl = 'search_%s_2nd'
    got_ptn_attr_name_tpl = 'got_%s'

    parsing_gb_attr_name = 'parsing_gb'
    parsing_gb_attr_name_2nd = 'parsing_gb_2nd'
    parsing_plan_attr_name = 'parsing_plan'
    parsing_plan_attr_name_2nd = 'parsing_plan_2nd'

    got_gb_attr_name = 'got_gb'
    got_plan_attr_name = 'got_plan'

    gb_ptn = re.compile(r"\d+ *gb(?![a-z])", re.I)
    tag_ptn = re.compile(r"<(\w+) *", re.I)

    def __init__(self, body):
        # self.body = body
        self.soup = BeautifulSoup(body, 'lxml')
        self.handlers = []
        # self.parse_body()

    def add_handler(self, handler):
        self.handlers.append(handler)
        return self

    def run_handlers(self):
        for handler in self.handlers:
            handler(self)
        return

    def get_GB_attrs(self):
        k_visited_parent = '_visited_parent'
        def el_checker(el):
            # 检查其父节点是否被访问过，若是，表示此 GB 节点与上一个GB 节点在同一 Plan 下
            # 因此忽略此节点
            parent = el.parent or {}
            if parent.get(k_visited_parent):
                return False
            if not check_specs(el):
                # detect some description that contains GB
                # print(text_with_space(el))
                words = filter_GB_words(text_with_space(el))
                # print(len(words), words)
                if len(words) > 5:
                    logger.debug('too many words: length=%s, words=%s' % (len(words), words))
                    return False
            parent[k_visited_parent] = True
            return True
        attrs = self.search_pattern(self.gb_ptn, 'gb', el_checker)
        return attrs

    def search_pattern_in_text(self, ptn, el, ptn_flag):
        els = []
        if not hasattr(el, 'contents'):
            if ptn.search(str(el)):
                return [el]
            return []
        if len(el.contents) == 0:
            if ptn.search(el.text):
                return [el]
            return []
        for child in el.contents:
            els += self.search_pattern_in_text(ptn, child, ptn_flag)
        return els

    def refresh_soup(self, soup=None):
        soup = soup or self.soup
        self.soup = BeautifulSoup(str(soup), 'lxml')
        return self.soup

    def search_pattern(self, ptn, ptn_flag, el_checker):
        """搜索 ptn, 并标记，返回所有标记"""
        assert ptn_flag.islower()

        def refresh_body(self):
            self.refresh_soup()
            body = self.soup.select('body')[0]
            body = str(body)
            return body

        i = 1
        search_pos = 0
        attrs = []
        while True:
            body = refresh_body(self)
            # 有可能搜到属性, 在调用 search_pattern 时要多考虑到这种情况
            # 比如用 search_pattern 搜索过一次 cpu，再搜第二次的时候
            result = ptn.search(body, search_pos)
            if not result:
                # logger.debug(body[:search_pos])
                logger.debug('search_pattern(%r) failed at pos %s' % (ptn, search_pos))
                # logger.debug(body[search_pos:])
                break

            # logger.debug('search_pattern succed: %s' % result)
            start, end = result.span()

            # find close tag after GB
            tag_search_pos = start - 3

            tag_idx = 0
            while True:
                if tag_search_pos <= 0:
                    raise Exception("error, can not fund any tag before %s", result)
                tag_res = self.tag_ptn.search(body[:start], tag_search_pos)
                if not tag_res:
                    tag_search_pos -= 3
                    continue
                # logger.debug('search tag succed: %s' % tag_res)
                tag_idx, _ = tag_res.span()
                tag_name = tag_res.group(1)
                tag_full_name = "<%s" % tag_name
                break
            # print(tag_res)

            # insert id into the open tag
            attr_name = self.search_ptn_attr_name_tpl % ptn_flag
            tag_attr = "%s=%d" % (attr_name, i)
            inserted_tag = "<%s %s " % (tag_name, tag_attr)
            # print(inserted_tag)
            # logger.debug('inserted_tag: %r, tag_full_name: %r' % (inserted_tag, tag_full_name))
            body = body[:tag_idx] + inserted_tag + body[tag_idx+len(tag_full_name):]

            # check if the tag contains GB info
            '''To avoid this:
            <strong>Premium Bandwidth -</strong> 250 GB @ 1gbps<br/>
            <strong>Type -</strong> Template<br/>
            '''
            _body = refresh_body(self)
            soup = str(self.soup).replace(str(_body), body)
            self.refresh_soup(soup)
            el = self.soup.select('[%s]' % (tag_attr))[0]
            # print('%r' % str(el))
            if not ptn.search(text_with_space(el)):
                # logger.debug('del el[%s]' % attr_name)
                del el[attr_name]
                el = el.parent
                while True:
                    # print('%r' % text_with_space(el))
                    if ptn.search(text_with_space(el)):
                        break
                    el = el.parent
                attr_name = self.search_ptn_attr_name_2nd_tpl % ptn_flag
                tag_attr = '%s=%d' % (attr_name, i)
                # logger.debug('el[%s]=%s' % (attr_name, i))
                el[attr_name] = i

            # print(el)
            # got GB node, check if contains more than GB info
            # contain_specs = sum([1 for e in el.children if 'gb' in e.text.lower()]) > 1

            succ = el_checker(el)
            if not succ:
                # logger.debug('el_checker failed, del: %s' % attr_name)
                del el[attr_name]
                body = refresh_body(self)
                pos = body[search_pos:].find(str(el))
                if pos < 0:
                    next_pos = body.find(str(el))
                    assert next_pos >= 0
                    pos = next_pos
                search_pos += pos + len(str(el))
                continue
            else:
                attr_name = self.got_ptn_attr_name_tpl % ptn_flag
                el[attr_name] = i

                body = refresh_body(self)
                el = self.soup.select('[%s]' % (tag_attr))[0]
                pos = body[search_pos:].find(str(el))
                """pos < 0 的情况：
                <a>
                    <b1>
                        <c1>20 GB</c1>
                    </b1>
                    <b2>20 GB</b2>
                </a> 
                此时 search_pos 在 b1 之后，而 el 则指向 a
                这样一来 find() 是找不到的
                """
                if pos < 0:
                    next_pos = body.find(str(el))
                    assert next_pos >= 0
                    pos = next_pos
                search_pos += pos + len(str(el))

            i += 1
            attrs.append(tag_attr)

        # bs4 有 bug 。。。。。
        # 如果不重新把 html 倒出来再倒进入的话，最后一次修改就无法 select 到
        self.refresh_soup()
        return attrs

    def get_plan_attrs(self, gb_tag_attrs):
        """获得 Plan 属性
        原理：首先找到 Plan 最小完整节点，打上属性标记，最后返回这个标记
        """
        gb_nodes = []
        soup = self.soup
        for tag_attr in gb_tag_attrs:
            gb_node = soup.select('[%s]' % tag_attr)[0]
            gb_nodes.append(gb_node)
        # 回溯父节点, 并打标记
        attr_name = self.parsing_plan_attr_name
        i = 1

        # 通过是否具有 “共同父节点” 来判断是否为 plan
        nodes = list(gb_nodes)
        unfound_nodes = []
        plan_tag_attrs = []
        while len(gb_nodes) > 1 and len(nodes):
            item_by_parent_attr = OrderedDict()
            parent_nodes = []
            j = 1
            parent_added = False
            last_attr = None
            for node in nodes:
                el = node.parent
                if not el:
                    _el = node
                    while hasattr(_el, '_x_from') and _el._x_from:
                        # print(_el._x_from)
                        _el = _el._x_from
                    unfound_nodes.append(_el)
                    continue
                el._x_from = node
                # print(i, j)

                attr_val = el.get(attr_name)
                if not attr_val:
                    attr_val = "level_%d-idx_%d" % (i, j)
                    el[attr_name] = attr_val

                attr = '%s=%s' % (attr_name, attr_val)
                sui = item_by_parent_attr.setdefault(attr, SearchUpItem(el))
                sui.add_child(node)
                j += 1
            i += 1

            nodes = []
            for attr, sui in item_by_parent_attr.items():
                logger.debug('attr:%s, count:%s', attr, len(sui.children))
                if len(sui.children) > 1:
                    for child in sui.children:
                        # 同一个 plan 内也可能出现 2 个 GB 节点共有父节点的情况
                        # 所以要检查下这个 child 是否真的包含有配置详情
                        if plan_detect(text_with_space(child)):
                            # 检查这个 plan 下的字数是否太多
                            txt = text_with_space(child)
                            words_cnt = len(txt.split())
                            if words_cnt > 2000:
                                logger.debug('plan_detected but too many words %d > 2000', words_cnt)
                                continue
                            logger.debug('plan_detect succ on (len=%d)%r', words_cnt, txt)
                            attr = '%s=%s' % (attr_name, child.get(attr_name))
                            if attr not in plan_tag_attrs:
                                plan_tag_attrs.append(attr)
                        else:
                            nodes.append(sui.parent)
                else:
                    nodes.append(sui.parent)
            logger.debug(plan_tag_attrs)

        # print(plan_tag_attrs)
        # print(unfound_nodes)
        nodes += unfound_nodes

        attr_name = self.parsing_plan_attr_name_2nd
        i = 1
        # 处理那些无法通过 “共同父节点” 来判断的节点
        for el in nodes:
            j = 1
            while True:
                succ = plan_detect(text_with_space(el))
                attr_val = "level_%d-idx_%d" % (i, j)
                el[attr_name] = attr_val

                tag_attr = '%s=%s' % (attr_name, attr_val)

                if succ:
                    plan_tag_attrs.append(tag_attr)
                    break

                el = el.parent
                if not el:
                    return []
                    # raise Exception("** ERROR reach top when search up for plan node")
                j += 1
            i += 1

        # 标记一下
        soup = self.refresh_soup()
        for i, attr in enumerate(plan_tag_attrs):
            el = soup.select('[%s]' % attr)[0]
            el[self.got_plan_attr_name] = i + 1

        return plan_tag_attrs

    def get_plans(self, plan_attrs):
        """获得 Plan 实例"""
        self.soup = BeautifulSoup(str(self.soup), 'lxml')
        soup = self.soup
        plans = []
        for attr in plan_attrs:
            el = soup.select('[%s]' % attr)[0]
            # 判断这个节点是不是包含了好几个plan
            if self.contains_multi_plan(el):
                logger.info('contains_multi_plan:True')
                plans += self.get_multi_plans(el)
            else:
                plans += [self.get_single_plan(el)]

        # logger.debug('plans:\n' + '\n\n'.join([str(plan) for plan in plans]))
        _plans = []
        for plan in plans:
            if plan.fields['price']:
                _plans.append(plan)

        if len(_plans) == 0 and len(plans) != 0:
            logger.warn('price not found')

        plans = _plans
        return plans

    def get_single_plan(self, plan_el):
        """获得 plan 节点内的单个 Plan
        有些 plan 节点会包含多个 Plan, 这种情况由 get_multi_plans 函数处理
        """
        plan = Plan()
        gb_el = plan_el.select('[%s]' % self.got_gb_attr_name)[0]
        # logger.debug('....... %r' % str(gb_el))
        concrete_els = []
        # 检查这个节点里面是否包含了多个 specs
        if plan_detect(gb_el):
            logger.debug('detected overlapped_plan in gb node')
            logger.debug('parsing plan_el: %s' % impact_els(plan_el))
            specs, concrete_els = self.get_overlapped_specs(gb_el.children)
            self._set_plan(plan, specs)
            concrete_els.append(gb_el)
        else:
            specs_els = self.get_spec_siblings(gb_el)
            # logger.debug('-'*4 + '%s', specs_els[0])
            specs = []

            logger.debug('parsing specs_els:\n' + impact_els(specs_els))
            for i, spec_el in enumerate(specs_els):
                spec = spec_detect(spec_el)
                if spec:
                    specs.append(spec)
                    concrete_els.append(spec_el)
            self._set_plan(plan, specs)

        # 可能还有些 specs 是在 gb_node 外面的，所以在 plan 节点再找一次
        self.get_outer_specs(plan_el, concrete_els, plan)

        logger.debug('successfully got plan:\n' + str(plan))
        return plan

    def get_outer_specs(self, plan_el, specs_els, plan):

        # 可能还有些 specs 是在 gb_node 外面的，所以在 plan 节点再找一次
        doc = str(plan_el)
        for el in specs_els:
            doc = doc.replace(str(el), '')
        new_plan_el = BeautifulSoup(doc, 'lxml')

        # logger.debug('before search_special_specs:\n' + str(plan))
        # 精确探测法
        search_special_specs(new_plan_el, plan)
        # logger.debug('after search_special_specs:\n' + str(plan))

        # 双值探测法
        els = destruct(new_plan_el)
        logger.debug("destruct plan_el: %r", len(els))
        specs, concrete_els = self.get_overlapped_specs(els)
        for spec in specs:
            old = plan.exists(spec)
            if old:
                logger.warn("duplicated spec: old:%r new:%r", old, spec)
            else:
                plan.set(spec)
                logger.debug("set new spec: %r", spec)

        # 有些 specs 如 name, price 可能会放在没有任何标识的节点里
        while True:
            logger.debug('----%r', oneline(new_plan_el))
            _els = extract_congener_node(new_plan_el)
            if len(_els) > 0:
                els = [el for el in _els if len(oneline(el)) > 0]
            else:
                els = []
                break
            for i, el in enumerate(els):
                logger.debug('::::::%r', str(el))
                if i == 0:
                    # 假定第一个是 plan name
                    el = els[0]
                    value_class = value_detect(el)
                    if value_class:
                        value = value_class.parse(el)
                        self._set_plan(plan, [value])
                        logger.debug('found new spec: %r', value)
                    else:
                        name = ValueDetectors.Name.parse(el)
                        self._set_plan(plan, [name])
                else:
                    value_class = value_detect(el)
                    if value_class:
                        value = value_class.parse(el)
                        logger.debug('found new spec: %r', value)
                        self._set_plan(plan, [value])

            if not plan.fields.get('price'):
                # 如果找不到 price，则把 name 也重置
                # 因为 price 和 name 往往在一个直接父节点下
                # 找不到 price 就意味着 name 很可能也是错的
                plan.fields['name'] = None
            doc = str(new_plan_el)
            for el in _els:
                doc = doc.replace(str(el), '')
            new_plan_el = BeautifulSoup(doc, 'lxml')


    def get_overlapped_specs(self, els):
        """获取层叠 specs
        原理：由于有些 plan 的 specs 并没有被节点包裹，而是形如：
              ```spec1 <br/> spec2```。我们称它为层叠specs。
              处理方式为使用 header_detect 和 value_detect 轮番探测, 选用较准确的结果 
        """
        specs = []

        headers = []
        values = []
        _els = []
        available_els = []
        for e in els:
            if oneline(e) == '':
                continue
            header = header_detect(e)
            value = value_detect(e)

            _els.append(e)
            headers.append(header)
            values.append(value)

        parsing_value = None
        for i in range(len(headers)):
            header = headers[i]
            value = values[i]
            result = None
            e = _els[i]

            if parsing_value:
                # 有未获得的 value
                result = parsing_value.check(e) and value_class.parse(e)
                if result:
                    specs.append(result)
                    available_els.append(e)
                    parsing_value = None
            else:
                if header:
                    # header 有效
                    value_class = get_value_class(header)
                    result = value_class.check(e) and value_class.parse(e)
                    if result:
                        # 能解析出 value 来
                        specs.append(result)
                    else:
                        # 不能的话，交给下一个
                        parsing_value = value_class
                    available_els.append(e)
            logger.debug('result:%r header:%r value:%r el:%r', result, header, value, oneline(e))
        return specs, available_els


        parsing_value = None
        for e in els:
            if oneline(e) == '':
                continue

            logger.debug("checking %r", oneline(e))
            if not parsing_value:
                header = header_detect(e)
                logger.debug("\theader1 result: %s" % header)
                if header:
                    parsing_value = get_value_class(header)
                    if parsing_value.check(e):
                        spec = parsing_value.parse(e)
                        specs.append(spec)
                        parsing_value = None
                        logger.debug("\twith value result: %s" % spec)
                # else: # 此项为复杂项，启用
            else:
                if not parsing_value.check(e):
                    header = header_detect(e)
                    logger.debug("\tvalue1 results: None(by %s)" % (parsing_value))
                    if header:
                        parsing_value = get_value_class(header)
                        logger.debug("\theader2 result: %s" % (header))
                    continue

                spec = parsing_value.parse(e)
                logger.debug("\tvalue2 results: %s" % spec)
                specs.append(spec)
                parsing_value = None
        return specs

    def get_non_structured_info(self, plan_el):
        """获得非结构化的信息
        原理：通过解析 dom tree，分析它的属性，比如 class, id 等，以此判断类别
        """
        specs = []
        # 探测 Price
        plan_el.select("[class*=price]")
        return specs

    def _set_plan(self, plan, specs):
        for spec in specs:
            old = plan.exists(spec)
            if old:
                logger.warn("duplicated spec, old:%r, new:%r" % (old, spec))
            else:
                plan.set(spec)


    def get_multi_plans(self, el):
        """返回多个 plans，这些 plans 都是共用 headers 的"""
        # 找出 header
        ptn = re.compile("cpu|core", re.I)
        def el_checker(el):
            return True
        # 因为可能多次搜索 cpu，则在第二次搜索的时候会搜到上一次标记的属性名
        # 所以不能用 search_pattern
        # cpu_attrs = self.search_pattern(ptn, 'cpu', el_checker)
        cpu_els = self.search_pattern_in_text(ptn, el, 'cpu')
        if len(cpu_els) != 1:
            lines = '\n'.join([ oneline(el) for el in cpu_els ])
            logger.error("searching aggregated plans, expect 1 cpu attrs, got %d, they are: \n%s" % (len(cpu_els), lines))
            return []
        cpu_el = cpu_els[0]
        header_els = self.get_spec_siblings(cpu_el)
        for i, s in enumerate(header_els):
            s['got_specs_siblings'] = i + 1

        # 识别出 header

        headers = headers_match(header_els)
        text = ''.join([ '\n\t%2d, %s' % (i, oneline(el)) for i, el in enumerate(header_els) ])
        logger.debug('headers:\n' + text + '\n')
        text = ''.join([ '\n\t%2d, %s' % (i, el) for i, el in enumerate(headers) ])
        logger.debug('detected headers:\n' + text + '\n')

        # 把 value 识别出来
        value_plans = []
        for gb_el in el.select('[%s]' % self.got_gb_attr_name):
            specs_els = self.get_spec_siblings(gb_el)
            value_plans.append(specs_els)

        # 去重
        upps = []
        got_plain_plan_attr_name = 'got_plain_plan'
        for i, specs_els in enumerate(value_plans):
            parent = specs_els[0].parent
            if parent.get(got_plain_plan_attr_name):
                continue
            parent[got_plain_plan_attr_name] = i+1
            upps.append(specs_els)
            # text = '\n'.join([text_with_space(el).replace('\n', ' ') for el in specs_els])
            # logger.debug('got No.%d plan:\n%s\n' % (i, impact_els(specs_els, '\n\t')))

        # 根据 headers 对 plain plans 对应的 spec 进行识别
        # 由于 headers 中并未识别出所有 spec, 所以仍需要对未识别的 specs 进行 detect
        plans = []
        for i, specs_els in enumerate(upps):
            plan = Plan()
            logger.debug('parsing No.%d plan:\n%s\n' % (i, impact_els(specs_els, '\n\t')))
            for j, header in enumerate(headers):
                if header:
                    value = get_value_class(header)
                    spec = value.parse(specs_els[j])
                    logger.debug("value %r parse result: %r, on %r", value, spec, oneline(specs_els[j]))
                else:
                    # 未识别的 header, 进行 detect
                    logger.debug('no pre-detected header for %r' % oneline(specs_els[j]))
                    spec = spec_detect(specs_els[j])
                if not spec:
                    continue
                old = plan.set(spec)
                if old:
                    logger.warn("duplicated spec, old:%r, new:%r" % (old, spec))
            logger.debug("parsed plan:\n\n%s\n" % str(plan))
            plans.append(plan)
        return plans

    def get_same_siblings(self, el):
        def checker(el, child):
            return el.name == child.name
        return self.get_siblings(el, checker)

    def get_spec_siblings(self, el):
        def checker(el, child):
            return el.name == child.name or spec_detect(child)
        return self.get_siblings(el, checker)

    def get_siblings(self, el, checker):
        siblings = []
        while True:
            parent = el.parent
            if not parent:
                raise Exception("reach top on el:%s", gb_el)
            children = []
            for child in parent.children:
                if checker(el, child):
                    children.append(child)

            # OK: 找到 specs 的共有父节点了
            if len(children) >= 3:
                siblings = children
                break
            el = parent
        return siblings

    def get_shared_parent(self, el):
        siblings = self.get_same_siblings(el)
        return siblings[0].parent

    def contains_multi_plan(self, el):
        """判断这个节点是不是包含了好几个plan
        策略1：提取 header 节点，判断是否包含具体数字，
        如果没有，则 header 位于 sidebar 内，
        且这是个多 plan 节点

        策略2：提取 GB 节点，判断是否包含说明文字，
        如果没有，则 GB 节点是一个共享 header 的节点

        注意：所提取的节点应该确保周围有3个以上兄弟节点
        """
        for gb_el in el.select('[%s]' % self.got_gb_attr_name):
            parent = self.get_shared_parent(gb_el)
            # 判断这个 specs 集合内是否包含说明文字
            has_desc = plan_detect(text_with_space(parent))
            if has_desc:
                return False
            return True

    def parse_body(self):
        gb_tag_attrs = list(self.get_GB_attrs())
        soup = self.soup
        for tag_attr in gb_tag_attrs:
            gb_node = soup.select('[%s]' % tag_attr)[0]
            # el = el.parent
            # print('-'*10, str(gb_node).replace('\n', '\\n'))
        plans = self.get_plans(gb_tag_attrs)


def filter_GB_words(text):
    striped_text = text
    for ptn in list(HeaderDetectors.Disk.keys + ValueDetectors.Disk.doubtless_keys + ValueDetectors.Disk.keys):
        if isinstance(ptn, str):
            ptn = re.compile(ptn, re.I)

        m = ptn.search(striped_text)
        if m:
            striped_text = ptn.sub('', striped_text)
            # start, end = m.span()
            # striped_text = striped_text[:start] + striped_text[end:]

    # print(text, '\n', striped_text)
    return striped_text.split()


class SearchUpItem(object):

    def __init__(self, parent):
        self.parent = parent
        self.children = []

    def add_child(self, child):
        self.children.append(child)


def destruct(el):
    """解构 node
    原理：如果对 el 进行 header_detect 发现有多个 header, 则分解为子节点
    """
    if not hasattr(el, 'children'):
        # logger.debug('--- no child: %s', el)
        return [el]

    els = []
    for c in el.children:
        try:
            header = header_detect(c)
            # logger.debug('destruct succ %s, %r', header, str(c))
            els.append(c)
        except MoreThanOneBest as e:
            # logger.debug('destruct fail %s, %r', None, str(c))
            els += destruct(c)
            logger.debug(e)

    # logger.debug('--- %d child', len(els))
    return els


def extract_congener_node(root_el, congener_threshold=3):
    """抽取同类节点
    原理：设有一段代码 `<ul><li></li><li></li></ul>`，则 li 为同类节点
    """
    if not hasattr(root_el, 'children'):
        return []

    sub_qualified_els = []

    for el in root_el.children:
        sub_direct_els = extract_congener_node(el, congener_threshold)
        if sub_direct_els:
            sub_qualified_els.append(sub_direct_els)

    sub_qualified_els = sorted(sub_qualified_els, key=lambda els: len(els))
    sub_qualified_els.reverse()
    sub_qualified_els = sub_qualified_els and sub_qualified_els[0]

    if sub_qualified_els:
        qualified_els = sub_qualified_els
    else:

        direct_els, _ = _get_congener_nodes(root_el, congener_threshold)
        direct_els = direct_els and direct_els[0]
        qualified_els = direct_els

    return qualified_els


def _get_congener_nodes(root_el, threshold=3):
    """获得 el 直接子元素中的同类节点，同时还会返回非同类节点"""
    if not hasattr(root_el, 'children'):
        return []

    congener_els = {}
    for el in root_el.children:
        if not el.name or el.name in ('br', 'option'):
            continue
        els = congener_els.setdefault(el.name, [])
        els.append(el)

    msg = '%r' % (str(root_el))
    logger.debug('{leading}root:{msg}'.format(**terracing(msg)))

    for name, els in congener_els.items():
        msg = '%s:%d' % (name, len(els))
        logger.debug('  {leading}{msg}'.format(**terracing(msg)))

    qualified_els = []
    unqualified_els = []
    for name, els in congener_els.items():
        if len(els) >= threshold:
            qualified_els.append(els)
        else:
            unqualified_els.append(els)

    def sorted_els(mels):
        mels = sorted(mels, key=lambda els: len(els))
        mels.reverse()
        return mels

    qualified_els = sorted_els(qualified_els)
    unqualified_els = sorted_els(unqualified_els)

    # logger.debug('......%s, %r', qualified_els, str(unqualified_els))

    return qualified_els, unqualified_els


def search_special_specs(plan_el, plan):
    if not plan.exists(HeaderDetectors.Name):
        el = HeaderDetectors.Name.select(plan_el)
        if el:
            value = ValueDetectors.Name.parse(el)
            plan.set(value)

    if not plan.exists(HeaderDetectors.Price):
        el = HeaderDetectors.Price.select(plan_el)
        logger.debug('found %r from plan:%r', str(el), str(plan_el))
        if el:
            value = ValueDetectors.Price.parse(el)
            plan.set(value)
