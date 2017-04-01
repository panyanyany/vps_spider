import re
from bs4 import BeautifulSoup


br_ptn = re.compile(r'<br */*>', re.I)
def text_subs_br(el):
    start_pos = 0
    doc = str(el)

    '''to avoid this:
    before:
        <br />Hard Drive: 40GB<br />IPv4: 1
    after:
        Hard Drive: 40GBIPv4: 1
    '''
    while True:
        el = BeautifulSoup(doc, 'lxml')
        m = br_ptn.search(doc, start_pos)
        if not m:
            return el.text

        start, end = m.span()
        doc = doc.replace(m.group(), '\n')
        # doc = doc.replace('\n', '\\n')
        # doc = doc.replace('\t', '\\t')
        start_pos = start + 2


def get_text(e):
    if hasattr(e, 'text'):
        # 'NavigableString' object has no attribute 'text'
        text = e.text
    else:
        text = str(e)
    return text


def text_with_space(el, inline=False):
    if not hasattr(el, 'contents'):
        # 'NavigableString' object has no attribute 'contents'
        return str(el)
    if len(el.contents) == 0:
        if el.name == 'br':
            return '\n'
        return el.text

    text_list = []
    for c in el.contents:
        text = text_with_space(c, inline)
        """
        leading = ''
        if c.name not in ('span', 'b', 'strong'):
            leading = ' '
        print('%r' % (c))
        print('%r, %r' % (leading, text))
        print('-'*10)
        """
        text_list.append(text)

    leading = ' '
    if inline and el.name in ('span', 'b', 'strong'):
        leading = ''
    return leading + ''.join(text_list) + leading

def impact_els(els, span='\n'):
    cs = []
    for el in els:
        text = text_with_space(el).strip()
        text = re.sub("\n[\n\t\s]+", '\n', text)
        if text:
            cs.append(text)
    return span + span.join(cs)

def clean_text(t, chars='\xa0\t\n'):
    for i in chars:
        t = t.replace(i, ' ')
    t = re.sub("\s+", ' ', t)
    return t.strip()

def oneline(el, inline=False):
    t = text_with_space(el, inline)
    t = clean_text(t)
    return t
