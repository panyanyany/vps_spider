import re

from .kit import PlanSet, PlanRange, FieldRange, ValueMatch, ValueSet, ValueSearch, ValuePipe, ExtractPrep
from libs.detectors import values

mapping = {
    'https://www.alpharacks.com/': [
        PlanSet([
            (('#third .server-package', 'header .h4'), {
                0: values.Name,
                1: values.Price,
            }),
            (('#third .server-package', 'ul li'), {
                0: ValueMatch(values.CPU, re.compile('(?P<core>\d+) ?x (?P<freq>\d+\.\d+)GHz')),
                1: values.RAM,
                2: values.Disk,
                3: ValuePipe(values.Traffic, 
                                     [ lambda t: t.replace(',', '').replace('.', '') + ' GB'],
                                 values.Traffic
                        ),
                4: values.NetworkOut,
                5: values.IP,
            }),
            (('body',), {
                0: [
                    ValueSet(values.Virt, vtype='KVM'),
                    # ValueSet(values.Location, loc=['Buffalo, NY', 'Los Angeles, CA', 'Dallas, TX', 'Chicago, IL', 'Seattle, WA', 'Frankfurt, Germany', 'Phoenix, AZ', 'Piscataway, NJ', 'San Jose, CA', 'Atlanta, GA']),
                    # ValueSet(values.DDoS, available=True, desc='New York Only'),
                ]
            }),
        ]),
        PlanSet([
            (('#second .server-package', 'header .h4'), {
                0: values.Name,
                1: values.Price,
            }),
            (('#second .server-package', 'ul li'), {
                0: ValueMatch(values.CPU, re.compile('(?P<core>\d+) ?x (?P<freq>\d+\.\d+)GHz')),
                1: values.RAM,
                2: values.Disk,
                3: ValuePipe(values.Traffic, 
                                     [ lambda t: t.replace(',', '').replace('.', '') + ' GB'],
                                 values.Traffic
                        ),
                4: values.IP,
                5: values.NetworkOut,
            }),
            (('body',), {
                0: [
                    ValueSet(values.Virt, vtype='KVM'),
                    # ValueSet(values.Location, loc=['Buffalo, NY', 'Los Angeles, CA', 'Dallas, TX', 'Chicago, IL', 'Seattle, WA', 'Frankfurt, Germany', 'Phoenix, AZ', 'Piscataway, NJ', 'San Jose, CA', 'Atlanta, GA']),
                    # ValueSet(values.DDoS, available=True, desc='New York Only'),
                ]
            }),
        ]),
        PlanSet([
            (('#first .server-package', 'header .h4'), {
                0: values.Name,
                # 1: values.Price,
            }),
            (('#first .server-package', 'ul li'), {
                0: values.RAM,
                1: values.Disk,
                2: ValuePipe(values.Traffic, 
                                     [ lambda t: t.replace(',', '').replace('.', '') + ' GB'],
                                 values.Traffic
                        ),
                3: values.IP,
                4: values.NetworkOut,
                6: values.Price,
            }),
            (('body',), {
                0: [
                    ValueSet(values.Virt, vtype='OpenVZ'),
                    ValueSet(values.CPU, core=1),
                    # ValueSet(values.Location, loc=['Buffalo, NY', 'Los Angeles, CA', 'Dallas, TX', 'Chicago, IL', 'Seattle, WA', 'Frankfurt, Germany', 'Phoenix, AZ', 'Piscataway, NJ', 'San Jose, CA', 'Atlanta, GA']),
                    # ValueSet(values.DDoS, available=True, desc='New York Only'),
                ]
            }),
        ]),
    ],
    'https://virmach.com/cheap-kvm-linux-vps-windows-vps/': PlanSet([
        (('.effect-scroll ul', 'li'), {
            0: values.Name,
            1: values.Price,
            2: values.RAM,
            3: ValueMatch(values.CPU, re.compile('@ (?P<freq>\w+)\+ GHz (?P<core>\w+) CPU')),
            4: values.Disk,
            5: (values.Traffic, values.NetworkOut),
            8: values.IP,
        }),
        (('body',), {
            0: [
                ValueSet(values.Virt, vtype='KVM'),
                ValueSet(values.Location, loc=['Buffalo, NY', 'Los Angeles, CA', 'Dallas, TX', 'Chicago, IL', 'Seattle, WA', 'Frankfurt, Germany', 'Phoenix, AZ', 'Piscataway, NJ', 'San Jose, CA', 'Atlanta, GA']),
                ValueSet(values.DDoS, available=True, desc='New York Only'),
            ]
        }),
    ]),
    'https://virmach.com/best-cheapest-linux-vps/': PlanSet([
        (('.effect-scroll ul', 'li'), {
            0: values.Name,
            1: values.Price,
            2: values.RAM,
            3: values.CPU,
            4: values.Disk,
            5: (values.Traffic, values.NetworkOut),
            8: values.IP,
        }),
        (('body',), {
            0: [
                ValueSet(values.Virt, vtype='OpenVZ'),
                ValueSet(values.Location, loc=['Buffalo, NY', 'Los Angeles, CA', 'Dallas, TX', 'Chicago, IL', 'Seattle, WA', 'Frankfurt, Germany', 'Phoenix, AZ', 'Piscataway, NJ', 'San Jose, CA', 'Atlanta, GA']),
                ValueSet(values.DDoS, available=True, desc='New York Only'),
            ]
        }),
    ]),
    'http://www.domain.com/hosting/vps/': PlanSet([
        (('#main > div.compgrid > table > tr', 'th', True, (1,)), {
            0: values.Name,
        }),
        (('#main > div.compgrid > table > tr', 'td', True, (1,)), {
            # 1: ValueSet(values.CPU, core=0),
            # 1: values.Name,
            # 0: values.Name,
            0: (values.RAM, ValueSet(values.CPU, core=0), ValueSet(values.Backup, enabled='yes')),
            1: values.Disk,
            2: values.Traffic,
            11: values.Price,
        }),
        (('body',), {
            0: [
                ValueSet(values.Location, loc=['Southfield, MI']),
            ]
        }),
    ]),
    'https://www.a2hosting.com/cloud-vps-hosting': PlanSet([
        (('#wrapper > section.features-block.page-piece-comparison.text-center.section-grey > div > div > div > div > div', 'div > div.heading-holder > h2'), {
            0: values.Name,
        }),
        (('#wrapper > section.features-block.page-piece-comparison.text-center.section-grey > div > div > div > div > div', 'div > div.holder > div.text > div.price-holder > span.price'), {
            0: values.Price,
        }),
        (('#wrapper > section.features-block.page-piece-comparison.text-center.section-grey > div > div > div > div > div', 'div > div.holder > div.text > div.description.e-description > ul > li'), {
            0: values.RAM,
            1: values.Disk,
            # 3: values.Disk,
            3: values.CPU,
            4: ValueMatch(values.CPU, re.compile("(?P<freq>\d+) (?P<freq_unit>\w+)")),
            # 13: values.Price,
        }),
        (('body',), {
            0: [
                ValueSet(values.Location, loc=['US', 'UK', 'Canada', 'France', 'India', 'Australia', 'Bangladesh', 'Brazil', 'China', 'Colombia', 'Germany', 'Indonesia', 'Israel', 'Italy', 'Japan', 'Malaysia', 'Mexico', 'Myanmar', 'Netherlands', 'Pakistan', 'Philippines', 'Poland', 'Russia', 'Singapore', 'South Korea', 'Spain', 'Sweden', 'Thailand', 'Turkey', 'Vietnam', ]),
            ]
        }),
    ]),
    'https://www.a2hosting.com/dedicated-server-hosting/semi': [
        PlanSet([
            (('#wrapper > section.features-block.page-piece-comparison.text-center.section-grey > div > div > div > div > div + div', 'div > div.heading-holder > h2'), {
                0: values.Name,
            }),
            (('#wrapper > section.features-block.page-piece-comparison.text-center.section-grey > div > div > div > div > div + div', 'div > div.holder > div.text > div.price-holder > span.price'), {
                0: values.Price,
            }),
            (('#wrapper > section.features-block.page-piece-comparison.text-center.section-grey > div > div > div > div > div + div', 'div > div.holder > div.text > div.description.e-description > ul > li'), {
                1: values.Disk,
                0: values.RAM,
                3: values.CPU,
                2: values.Traffic,
            }),
            (('body',), {
                0: [
                    ValueSet(values.Location, loc=['US', 'UK', 'Canada', 'France', 'India', 'Australia', 'Bangladesh', 'Brazil', 'China', 'Colombia', 'Germany', 'Indonesia', 'Israel', 'Italy', 'Japan', 'Malaysia', 'Mexico', 'Myanmar', 'Netherlands', 'Pakistan', 'Philippines', 'Poland', 'Russia', 'Singapore', 'South Korea', 'Spain', 'Sweden', 'Thailand', 'Turkey', 'Vietnam', ]),
                ]
            }),
        ]),
    ],
    'https://www.a2hosting.com/dedicated-server-hosting/unmanaged': [
        PlanSet([
            (('#wrapper > section.features-block.page-piece-comparison.text-center.section-grey > div > div > div > div > div + div', 'div > div.heading-holder > h2'), {
                0: values.Name,
            }),
            (('#wrapper > section.features-block.page-piece-comparison.text-center.section-grey > div > div > div > div > div + div', 'div > div.holder > div.text > div.price-holder > span.price'), {
                0: values.Price,
            }),
            (('#wrapper > section.features-block.page-piece-comparison.text-center.section-grey > div > div > div > div > div + div', 'div > div.holder > div.text > div.description.e-description > ul > li'), {
                1: values.Disk,
                0: values.RAM,
                3: values.CPU,
                4: ValueMatch(values.CPU, re.compile("(?P<freq>\d+.\d+)\+ (?P<freq_unit>\wHz)")),
                2: values.Traffic,
            }),
            (('body',), {
                0: [
                    ValueSet(values.Location, loc=['US', 'UK', 'Canada', 'France', 'India', 'Australia', 'Bangladesh', 'Brazil', 'China', 'Colombia', 'Germany', 'Indonesia', 'Israel', 'Italy', 'Japan', 'Malaysia', 'Mexico', 'Myanmar', 'Netherlands', 'Pakistan', 'Philippines', 'Poland', 'Russia', 'Singapore', 'South Korea', 'Spain', 'Sweden', 'Thailand', 'Turkey', 'Vietnam', ]),
                ]
            }),
        ]),
    ],
    'http://webservices.thesba.com/ssd-linux-vps/': PlanSet([
        (('#tbl-rw-3-1 > div.title-main > div', 'div > span'), {
            0: values.Name,
            1: values.Price,
        }),
        (('#tbl-rw-3-1 > div', 'div > ul > li'), {
            0: values.Disk,
            1: values.RAM,
            # 2: values.Traffic,
            3: values.CPU,
            # 13: values.Price,
        }),
    ]),
    'https://blazingfast.io/vps': [
        PlanSet([
            (('body > section.smallplans > div > div > div', 'div > p'), {
                0: values.Price,
            }),
            (('body > section.smallplans > div > div > div', 'div > ul > li'), {
                0: ValueMatch(values.CPU, re.compile("(?P<core>\d+) CPU[^\d]+(?P<freq>\d.\d)\+ (?P<freq_unit>\wHz)")),
                1: values.RAM,
                2: values.Disk,
                4: values.NetworkOut,
            }),
        ]),
        PlanSet([
            (('body > section.lightblue > div > div > div', 'div > p'), {
                0: values.Price,
            }),
            (('body > section.lightblue > div > div > div', 'div > ul > li'), {
                0: ValueMatch(values.CPU, re.compile("(?P<core>\d+) CPU[^\d]+(?P<freq>\d.\d)\+ (?P<freq_unit>\wHz)")),
                1: values.RAM,
                2: values.Disk,
                4: values.NetworkOut,
            }),
        ]),
    ],
    'https://turnkeyinternet.net/cloud-hosted-virtual-servers-vps/': [
        PlanSet([
            (('#main-container > div.table > div > table > tbody > tr:nth-child(1) > th', 'div.pricing-plan-price'), {
                0: values.Price,
            }),
            (('#main-container > div.table > div > table > tbody > tr', 'td + td', True), {
                0: values.CPU,
                1: values.RAM,
                2: values.Disk,
                3: values.NetworkOut,
                5: ValueSet(values.IP, ipv4=1),
                6: ValueSet(values.IP, ipv6=1, ipv6_fp=64, relation='and'),
                7: ValueSet(values.IP, ipv6=1, ipv6_fp=64, relation='and'),
            }),
            (('body',), {
                0: ValueSet(values.Traffic, volume=0),
            })
        ]),
    ],
    'https://www.runabove.com/VPS-HDD.xml': [
        PlanSet([
            (('#main > div:nth-of-type(6) > div > div:nth-of-type(2) > div', 'div.BlockPrice > div.monthly > div > span'), {
                0: values.Price,
            }),
            (('#main > div:nth-of-type(6) > div > div:nth-of-type(2) > div', '> ul > li'), {
                0: values.Name,
                1: values.CPU,
                2: values.RAM,
                3: values.Disk,
                5: values.Traffic,
            }),
        ]),
    ],
    'https://www.runabove.com/cloud-instance.xml': [
        PlanSet([
            (('#main > div:nth-of-type(6) > div > div:nth-of-type(2) > div', 'div.BlockPrice > div.monthly > div > span'), {
                0: values.Price,
            }),
            (('#main > div:nth-of-type(6) > div > div:nth-of-type(2) > div', '> ul > li'), {
                0: values.Name,
                1: values.CPU,
                2: values.RAM,
                3: values.Disk,
                5: values.Traffic,
            }),
        ]),
    ],
    'https://www.iwfhosting.net/vps': [
        PlanSet([
            (('#sharedhost > div > table > thead:nth-child(1) > tr', 'th + th', True), {
                0: values.Name,
            }),
            (('#sharedhost > div > table > tbody:nth-of-type(1) > tr', 'td + td', True), {
                0: values.Disk,
                1: values.Traffic,
                2: values.RAM,
                3: values.CPU,
                4: ValueMatch(values.IP, re.compile("(?P<ipv4>\d+)")),
                6: values.Price,
            }),
        ]),
    ],
    'https://www.iwfhosting.net/dedicated': [
        PlanSet([
            (('#dedicatedhost > div.table-responsive > table > tbody > tr + tr', 'td'), {
                2: ValueMatch(values.Disk, re.compile("((?P<disk_cnt>\d+)x ?)?(?P<size>\d+)(?P<size_unit>\w+) (?P<disk_type>SSD)")),
                1: values.RAM,
                0: ValueMatch(values.CPU, re.compile("(?P<manuf>[\w\d ]+[\w\d]+) \((?P<core>\d+).*?\)")),
                4: [
                    values.Traffic,
                    values.NetworkOut,
                ],
                5: [
                    ValueMatch(values.IP, re.compile("(?P<ipv4>\d+) IPv4 \+ /(?P<ipv6_fp>\d+)")),
                    ValueSet(values.IP, ipv6=1, relation='and'),
                ],
                6: values.Price,
            }),
        ]),
    ],
    'https://www.stablehost.com/table.php': [
        PlanSet([
            (('body > div.wrapper > div.container > section > div > div.section-body > div > table > tr', 'td'), {
                0: values.Name,
                1: values.RAM,
                2: values.CPU,
                3: values.Disk,
                4: values.Traffic,
                6: values.Price,
            }),
        ]),
    ],
    'http://cheapwindowsvps.com/': [
        PlanSet([
            (('#plans > div > div', 'div.plan_main > ul > li'), {
                0: values.RAM,
                1: values.Disk,
                2: values.CPU,
            }),
            (('#plans > div > div', '> div:nth-child(3) > *'), {
                0: values.Price,
                1: [values.Traffic, values.NetworkOut],
            }),
        ]),
    ],
    'https://www.eurovps.com/linux-vps': [
        PlanSet([
            (('#t-2 > div > div > div > div', 'div.head > strong'), {
                0: values.Name,
            }),
            (('#t-2 > div > div > div > div', 'div.body > form > div.price'), {
                0: [values.Price, ValueSet(values.Price, currency_code='EUR')],
            }),
            (('#t-2 > div > div > div > div', 'div.body > form > p > strong'), {
                0: values.RAM,
                1: values.CPU,
                2: ValueMatch(values.CPU, re.compile("(?P<freq>\d+.?\d+)(?P<freq_unit>\wHz)")),
                3: [
                    values.Disk,
                    ValueSet(values.Disk, disk_type='SSD'),
                ],
                5: values.Traffic,
            }),
        ]),
    ],
    'https://www.eurovps.com/dedicated-servers': [
        PlanSet([
            (('.dedicated-server-table table tr + tr', 'td'), {
                0: ValueMatch(values.CPU, re.compile('(?P<manuf>.+)')),
                1: values.CPU,
                2: ValueMatch(values.CPU, re.compile('(?P<freq>\d+.?\d+)(?P<freq_unit>\wHz)')),
                4: values.RAM,
                5: ValueMatch(values.Disk, re.compile('(?P<disk_cnt>\d+) x (?P<size>\d+)(?P<size_unit>\w+) (?P<disk_type>SSD)')),
                6: values.Traffic,
                7: [
                    ValueMatch(values.Price, re.compile('(?P<price>\d+\.?\d*)(?P<currency_symb>.)')),
                    ValueSet(values.Price, currency_code='EUR'),
                ]
            }),
        ]),
    ],
    'https://libertyvps.net/offshore-vps': [
        PlanSet([
            (('#main > div > div > div.uds-pricing-table.default > table > thead > tr:nth-child(2) > th', 'h3,p',), {
                0: values.Name,
                1: values.Price,
            }),
            (('#main > div > div > div.uds-pricing-table.default > table > tbody > tr', 'td', True), {
                0: values.CPU,
                1: values.RAM,
                2: values.Disk,
                3: values.Traffic,
                4: values.NetworkOut,
                5: ValueMatch(values.Virt, re.compile("Linux (?P<vtype>\w+)")),
                8: ValueMatch(values.Location, re.compile("The (?P<loc>\w+)")),
            }),
        ]),
    ],
    'https://www.hawkhost.com/vps-hosting': [
        PlanSet([
            (('#anch-1 > div > div > a', 'div > div > div.bx-semi-price > h4'), {
                0: values.Price,
            }),
            (('#anch-1 > div > div > a', 'div > div > div.box-semi-content > ul > li'), {
                1: values.RAM,
                3: values.Disk,
                4: values.Traffic,
            }),
            (('#anch-1 > div > div > a', 'div > div > div.box-semi-content > ul'), {
                0: ValueSet(values.CPU, core=0),
            }),
            (('body',), {
                0: [
                    ValueSet(values.Virt, vtype='OpenVZ'),
                    # ValueSet(values.Location, loc=['Buffalo, NY', 'Los Angeles, CA', 'Dallas, TX', 'Chicago, IL', 'Seattle, WA', 'Frankfurt, Germany', 'Phoenix, AZ', 'Piscataway, NJ', 'San Jose, CA', 'Atlanta, GA']),
                    # ValueSet(values.DDoS, available=True, desc='New York Only'),
                ]
            }),
        ]),
    ],
    'https://www.jaguarpc.com/cloud-vps-hosting/': [
        PlanSet([
            (('body > section.cm-hosting-plan.cm-hosting-block-tab > div > div > div > div:nth-child(2) > div > table > tbody > tr', 'td'), {
                0: values.CPU,
                1: values.Disk,
                2: values.RAM,
                3: values.Traffic,
                4: values.Price,
            }),
        ]),
        PlanSet([
            (('body > section.cm-hosting-plan.cm-hosting-block-tab > div > div > div > div:nth-of-type(1) > div > table > tbody > tr th', '.rate'), {
                0: values.Price,
            }),
            (('body > section.cm-hosting-plan.cm-hosting-block-tab > div > div > div > div:nth-of-type(1) > div > table > tbody > tr + tr', 'td + td', True), {
                0: values.Disk,
                1: values.RAM,
                2: values.CPU,
                3: ValuePipe(values.Traffic, 
                                 [ lambda t: t.replace(',', '').replace('.', '') + ' GB'],
                             values.Traffic
                    ),
                4: ValueMatch(values.IP, re.compile("(?P<ipv4>\d+)")),
                5: [
                    ValueMatch(values.IP, re.compile("(?P<ipv6>\d+)")),
                    ValueSet(values.IP, relation='and'),
                ],
            }),
        ]),
    ],
    'https://amazonlightsail.com/pricing/': [
        PlanSet([
            (('#content > main > div.pricing > div > div', 'h4 > span'), {
                0: values.Price,
            }),
            (('#content > main > div.pricing > div > div', 'ul > li'), {
                0: values.RAM,
                1: values.CPU,
                2: values.Disk,
                3: values.Traffic,
            }),
        ]),
    ],
    'https://hostus.us/kvm-vps.html': [
        PlanSet([
            (('#pricing > div > div.row.no-pad > div:nth-child(1) > div.col-sm-10 > div', 'div > div'), {
                0: values.Name,
                1: values.Price,
            }),
            (('body > footer > div > div > div:nth-child(2)', 'ul'), {
                0: ValueMatch(values.Location, re.compile("(?P<loc>.*)")),
            }),
            (('#pricing > div > div.row.no-pad > div:nth-child(1) > div.col-sm-10 > div', 'div > ul > li'), {
                0: values.CPU,
                1: values.Disk,
                2: values.RAM,
                3: values.Traffic,
                4: ValueMatch(values.IP, re.compile("(?P<ipv4>\d+) IPv4 / (?P<ipv6>\d+) IPv6")),
            }),
        ]),
    ],
    'https://hostus.us/managed-vps.html': [
        PlanSet([
            (('#pricing > div > div.row > div + div > div', '*'), {
                1: values.Name,
                2: values.Price,
            }),
            (('#pricing > div > div.row > div + div .plan-desc ul', 'li'), {
                0: values.RAM,
                1: values.VSwap,
                2: values.Disk,
                3: values.CPU,
                4: values.Traffic,
                5: ValueMatch(values.IP, re.compile("(?P<ipv4>\d+) IPv4")),
                6: ValueMatch(values.IP, re.compile("(?P<ipv6>\d+) IPv6")),
            }),
        ]),
    ],
    'http://www.impactvps.com/vps.html': [
        PlanSet([
            (('div.contentbox.paddingbox.gurantee-box > section > article > div > aside', '> *'), {
                0: values.Name,
                1: values.Price,
            }),
            (('div.contentbox.paddingbox.gurantee-box > section > article > div > aside', 'ul > li'), {
                0: values.CPU,
                1: values.RAM,
                2: values.Disk,
                3: values.Traffic,
                4: ValueMatch(values.IP, re.compile("(?P<ipv4>\d+)")),
                5: ValueMatch(values.Location, re.compile("(?P<loc>\w+)")),
            }),
        ]),
    ],
    'http://www.impactvps.com/storagevps.html': [
        PlanSet([
            (('#carusal aside', '> *'), {
                0: values.Name,
                1: values.Price,
            }),
            (('#carusal aside', 'ul > li'), {
                0: values.CPU,
                1: values.RAM,
                2: values.Disk,
                3: values.Traffic,
                4: ValueMatch(values.IP, re.compile("(?P<ipv4>\d+)")),
                # 5: ValueMatch(values.Location, re.compile("(?P<loc>\w+)")),
            }),
        ]),
    ],
    'https://www.servint.net/product/vps/': [
        PlanSet([
            (('#product > div.page-intro.tight > div > table:nth-of-type(1) > tbody > tr', 'td'), {
                0: [values.Name, ValueSet(values.CPU, core=1)],
                1: values.RAM,
                2: values.Disk,
                3: ValueMatch(values.IP, re.compile('(?P<ipv4>\d+)')),
                4: values.Traffic,
                5: values.Price,
            }),
        ]),
        PlanSet([
            (('#product > div.page-intro.tight > div > table:nth-of-type(2) > tbody > tr', 'td'), {
                0: [ValueMatch(values.CPU, re.compile('(?P<freq>\d+\.\d+)')), ValueSet(values.CPU, core=1)],
                1: values.RAM,
                2: values.Disk,
                3: ValueMatch(values.IP, re.compile('(?P<ipv4>\d+)')),
                4: values.Traffic,
                5: values.Price,
            }),
        ]),
    ],
    'https://www.servint.net/dedicated/': [
        PlanSet([
            (('table > tbody > tr', 'td'), {
                0: values.CPU,
                1: values.RAM,
                2: values.Disk,
                3: ValueMatch(values.IP, re.compile('(?P<ipv4>\d+)')),
                4: values.Traffic,
                5: values.Price,
            }),
        ]),
    ],
    'https://www.vpsserver.com/plans/': [
        PlanSet([
            (('div.plan-base.normal-plan > div', '> *'), {
                0: ValueMatch(values.Price, re.compile("(?P<price>\d+)")),
                5: ValueMatch(values.Trial, {'days': (re.compile("(?P<days>\d+)"), 0)}),
            }),
            (('div.plan-base.normal-plan > div', '.single-spec'), {
                0: values.RAM,
                1: values.CPU,
                2: values.Disk,
                3: values.Traffic,
            }),
        ]),
        PlanSet([
            (('div.plan-base.premium-plan > div', '> *'), {
                0: ValueMatch(values.Price, re.compile("(?P<price>\d+)")),
                5: ValueMatch(values.Trial, {'days': (re.compile("(?P<days>\d+)"), 0)}),
            }),
            (('div.plan-base.premium-plan > div', '.single-spec'), {
                0: values.RAM,
                1: values.CPU,
                2: values.Disk,
                3: values.Traffic,
            }),
        ]),
    ],
    'https://www.cloudsigma.com/pricing/': [
        PlanSet([
            (('.x-pricing-column', 'h2'), {
                0: values.Name,
            }),
            (('.x-pricing-column > div', 'h3'), {
                0: values.Price,
            }),
            (('.x-pricing-column > div > ul', 'li'), {
                0: values.CPU,
                1: values.RAM,
                2: values.Disk,
                3: values.Traffic,
            }),
        ]),
    ],
    'https://www.host1plus.com/vps-hosting/': [
        PlanSet([
            (('div.plans-pricing-table > div', 'form > div:nth-child(1) > div'), {
                0: values.Name,
            }),
            (('div.plans-pricing-table > div', 'form > div:nth-child(1) .price > .main-price'), {
                0: values.Price,
            }),
            (('div.plans-pricing-table > div', 'form > div:nth-child(2) > div'), {
                0: ValueMatch(values.CPU, re.compile('(?P<core>\d+\.?\d*)')),
                1: values.RAM,
                2: values.Disk,
                3: values.Traffic,
            }),
        ]),
    ],
    'https://www.host1plus.com/cloud-servers/': [
        PlanSet([
            (('div.plans-pricing-table > div', 'form > div:nth-child(1) > div'), {
                0: values.Name,
            }),
            (('div.plans-pricing-table > div', 'form > div:nth-child(1) .price > .main-price'), {
                0: values.Price,
            }),
            (('div.plans-pricing-table > div', 'form > div:nth-child(2) > div'), {
                0: values.CPU,
                1: values.RAM,
                2: values.Disk,
                3: values.Traffic,
            }),
        ]),
    ],
    'https://www.linode.com/pricing': [
        PlanSet([
            (('#pricing-larger-plans > div > div > div > div > table > tbody > tr', 'td'), {
                0: values.Name,
                1: values.RAM,
                2: values.CPU,
                3: values.Disk,
                4: values.Traffic,
                5: values.NetworkIn,
                6: values.NetworkOut,
                7: values.Price,
            }),
            (('body',), {
                0: [
                    ValueSet(values.Virt, vtype='KVM'),
                    # ValueSet(values.Location, loc=['Buffalo, NY', 'Los Angeles, CA', 'Dallas, TX', 'Chicago, IL', 'Seattle, WA', 'Frankfurt, Germany', 'Phoenix, AZ', 'Piscataway, NJ', 'San Jose, CA', 'Atlanta, GA']),
                    # ValueSet(values.DDoS, available=True, desc='New York Only'),
                ]
            }),
        ]),
    ],
    'https://www.arubacloud.com/vps/virtual-private-server-range.aspx': [
        PlanSet([
            (('.table-sizes-box > div', 'table thead tr th strong'), {
                0: values.Name,
            }),
            (('.table-sizes-box > div', 'table thead tr th .table-price'), {
                0: [values.Price, ValueSet(values.Price, currency_code='EUR')],
            }),
            (('.table-sizes-box > div', 'table tbody tr'), {
                1: values.CPU,
                2: values.RAM,
                3: values.Disk,
                4: values.Traffic,
            }),
            (('body',), {
                0: [
                    ValueSet(values.Virt, vtype='VMware'),
                    # ValueSet(values.Location, loc=['Buffalo, NY', 'Los Angeles, CA', 'Dallas, TX', 'Chicago, IL', 'Seattle, WA', 'Frankfurt, Germany', 'Phoenix, AZ', 'Piscataway, NJ', 'San Jose, CA', 'Atlanta, GA']),
                    # ValueSet(values.DDoS, available=True, desc='New York Only'),
                ]
            }),
        ]),
    ],
    'http://www.ramnode.com/vps.php': [
        PlanSet([
            (('#vzdiv table tbody tr', 'td'), {
                0: values.Name,
                1: values.RAM,
                2: values.CPU,
                3: ValueMatch(values.IP, re.compile('(?P<ipv4>\d+)')),
                4: ValueMatch(values.IP, re.compile('(?P<ipv6_fp>\d+)')),
                5: values.Disk,
                6: values.Traffic,
                7: values.Price,
            }),
            (('body',), {
                0: [
                    ValueSet(values.NetworkOut, speed=1, speed_unit='Gbps'),
                    ValueSet(values.Virt, vtype='OpenVZ'),
                ],
            }),
        ]),
        PlanSet([
            (('#kvmdiv table tbody tr', 'td'), {
                0: values.Name,
                1: values.RAM,
                2: values.CPU,
                3: ValueMatch(values.IP, re.compile('(?P<ipv4>\d+)')),
                4: ValueMatch(values.IP, re.compile('(?P<ipv6_fp>\d+)')),
                5: values.Disk,
                6: values.Traffic,
                7: values.Price,
            }),
            (('body',), {
                0: [
                    ValueSet(values.NetworkOut, speed=1, speed_unit='Gbps'),
                    ValueSet(values.Virt, vtype='KVM'),
                ],
            }),
        ]),
    ],
    'http://www.ramnode.com/vds.php': [
        PlanSet([
            (('table tbody tr', 'td'), {
                0: values.Name,
                1: values.RAM,
                2: values.CPU,
                3: ValueMatch(values.IP, re.compile('(?P<ipv4>\d+)')),
                4: ValueMatch(values.IP, re.compile('(?P<ipv6_fp>\d+)')),
                5: values.Disk,
                6: values.Traffic,
                7: values.Price,
            }),
            (('body',), {
                0: ValueSet(values.NetworkOut, speed=1, speed_unit='Gbps'),
            }),
        ]),
    ],
    'https://www.namecheap.com/hosting/vps.aspx': [
        PlanSet([
            (('.product-grid > div', 'h2'), {
                0: values.Name,
            }),
            (('.product-grid > div', '.price'), {
                0: values.Price,
            }),
            (('#ctl00_ctl00_ctl00_ctl00_base_content_web_base_content_currencyDisplay',), {
                0: ValueMatch(values.Price, re.compile('(?P<currency_code>\w+)')),
            }),
            (('.product-grid > div', 'ul li'), {
                0: values.RAM,
                1: values.CPU,
                2: values.Disk,
                3: values.Traffic,
            }),
        ]),
    ],
    'https://www.namecheap.com/hosting/dedicated-servers.aspx': [
        PlanSet([
            (('#ctl00_ctl00_ctl00_ctl00_base_content_web_base_content_currencyDisplay',), {
                0: ValueMatch(values.Price, re.compile('(?P<currency_code>\w+)')),
            }),
            (('.server-list div > ul', 'li'), {
                1: values.RAM,
                0: [values.CPU, ValueMatch(values.CPU, re.compile('(?P<freq>\d+\.\d+)'))],
                2: [
                    values.Disk,
                    ValuePipe(values.Disk, 
                                 [ lambda t: '1 x ' + t if ' x ' not in t else t, ],
                                 ValueMatch(values.Disk, re.compile('(?P<disk_cnt>\d+) x')),
                    ),
                ],
                3: values.Traffic,
                4: ValuePipe(values.Price, [
                    lambda t: t.replace(',', ''),
                    ExtractPrep('([^ \d]) +(\d+) +([\d\.]+)', '{0} {1}{2}'),
                ]),
            }),
        ]),
    ],
    'https://www.digitalocean.com/pricing/': [
        PlanSet([
            (('.PriceBlocks-slider > div', '.PriceBlock-top'), {
                0: values.Price,
            }),
            (('.PriceBlocks-slider > div', 'ul li'), {
                0: values.RAM,
                1: values.CPU,
                2: values.Disk,
                3: values.Traffic,
            }),
            (('body',), {
                0: [
                    ValueSet(values.Virt, vtype='KVM'),
                    # ValueSet(values.Location, loc=['Buffalo, NY', 'Los Angeles, CA', 'Dallas, TX', 'Chicago, IL', 'Seattle, WA', 'Frankfurt, Germany', 'Phoenix, AZ', 'Piscataway, NJ', 'San Jose, CA', 'Atlanta, GA']),
                    # ValueSet(values.DDoS, available=True, desc='New York Only'),
                ]
            }),
        ]),
    ],
    'http://www.hostgator.com/vps-hosting': [
        PlanSet([
            (('#compare-plans thead th + th', 'h2, h3'), {
                0: values.Name,
                1: values.Price,
            }),
            (('#compare-plans tbody tr', 'td + td', True), {
                1: values.RAM,
                0: values.CPU,
                2: values.Disk,
                3: values.Traffic,
                4: ValueMatch(values.IP, re.compile('(?P<ipv4>\d+)')),
                # 3: values.NetworkOut,
                # 8: values.Price,
            }),
        ]),
    ],
    'http://www.hostgator.com/dedicated-server': [
        PlanSet([
            (('#comparision-chart tr', 'th + th', True), {
                0: values.Name,
            }),
            (('#comparision-chart tr', 'td + td', True), {
                4: values.RAM,
                1: values.CPU,
                2: ValuePipe(values.CPU, [], ValueMatch(values.CPU, re.compile('(?P<freq>\d+\.\d+)'))),
                5: values.Disk,
                6: values.Traffic,
                7: ValueMatch(values.IP, re.compile('(?P<ipv4>\d+)')),
                3: values.NetworkOut,
                8: values.Price,
            }),
        ]),
    ],
    'https://bwh1.net/vps-hosting.php': [
        PlanSet([
            (('.bronze', 'h2', ), {
                0: values.Name,
            }),
            (('.bronze', 'li', ), {
                1: values.RAM,
                4: ValuePipe(values.CPU, [], ValueMatch(values.CPU, re.compile('(?P<core>\d+)'))),
                0: values.Disk,
                3: values.Traffic,
                7: ValueMatch(values.Virt, re.compile('(?P<vtype>OpenVZ)')),
                5: values.NetworkOut,
                10: values.Price,
                2: values.VSwap,
            }),
        ]),
    ],
    'https://www.providerservice.com/products/virtual-servers/': [
        PlanSet([
            (('table tr + tr', 'td', ), {
                0: values.CPU,
                1: values.RAM,
                2: values.Disk,
                4: values.Traffic,
                # 5: ValueMatch(values.Price, re.compile('(?P<period>\d+)')),
                6: [values.Price, ValueSet(values.Price, currency_code='EUR')],
            }),
            (('body',), {
                0: [
                    ValueSet(values.Virt, vtype='KVM'),
                    # ValueSet(values.Location, loc=['Buffalo, NY', 'Los Angeles, CA', 'Dallas, TX', 'Chicago, IL', 'Seattle, WA', 'Frankfurt, Germany', 'Phoenix, AZ', 'Piscataway, NJ', 'San Jose, CA', 'Atlanta, GA']),
                    # ValueSet(values.DDoS, available=True, desc='New York Only'),
                ]
            }),
        ]),
    ],
    'https://www.providerservice.com/products/cloud-server/': [
        PlanSet([
            (('.tableBox', '> div', ), {
                0: values.Name,
            }),
            (('.tableBox', 'ul li', ), {
                0: values.CPU,
                1: values.RAM,
                2: [values.Disk, ValueSet(values.Disk, disk_type='SSD')],
                3: [ValueMatch(values.IP, re.compile('(?P<ipv4>\d+)'))],
                4: [ValueMatch(values.IP, re.compile('(?P<ipv6>\d+)'))],
                5: values.Traffic,
                7: [ValueMatch(values.Price, re.compile('(?P<price>\d+\.\d+)')), ValueSet(values.Price, currency_code='EUR', currency_symb='€')],
            }),
            (('body',), {
                0: [
                    ValueSet(values.Virt, vtype='KVM'),
                    # ValueSet(values.Location, loc=['Buffalo, NY', 'Los Angeles, CA', 'Dallas, TX', 'Chicago, IL', 'Seattle, WA', 'Frankfurt, Germany', 'Phoenix, AZ', 'Piscataway, NJ', 'San Jose, CA', 'Atlanta, GA']),
                    # ValueSet(values.DDoS, available=True, desc='New York Only'),
                ]
            }),
        ]),
    ],
    'https://www.providerservice.com/products/managed-servers/': [
        PlanSet([
            (('.tableBox', '> div', ), {
                0: values.Name,
            }),
            (('.tableBox', 'ul li', ), {
                0: values.CPU,
                1: values.RAM,
                2: [values.Disk, ValueSet(values.Disk, disk_type='SSD')],
                3: [ValueMatch(values.IP, re.compile('(?P<ipv4>\d+)'))],
                4: [ValueMatch(values.IP, re.compile('(?P<ipv6>\d+)'))],
                5: values.Traffic,
                7: [ValueMatch(values.Price, re.compile('(?P<price>\d+\.\d+)')), ValueSet(values.Price, currency_code='EUR', currency_symb='€')],
            }),
            (('body',), {
                0: [
                    ValueSet(values.Virt, vtype='KVM'),
                    # ValueSet(values.Location, loc=['Buffalo, NY', 'Los Angeles, CA', 'Dallas, TX', 'Chicago, IL', 'Seattle, WA', 'Frankfurt, Germany', 'Phoenix, AZ', 'Piscataway, NJ', 'San Jose, CA', 'Atlanta, GA']),
                    # ValueSet(values.DDoS, available=True, desc='New York Only'),
                ]
            }),
        ]),
    ],
    'https://www.providerservice.com/products/dedicated-servers/': [
        PlanSet([
            (('.table tr + tr', 'td', ), {
                0: [
                    ValuePipe(values.CPU, 
                                 [ lambda t: '1x ' + t if t[1] != 'x' else t, ],
                                 ValueMatch(values.CPU, re.compile('(?P<cpu_cnt>\d+)x.*?(?P<core>\d+)x (?P<freq>\d+\.\d+) GHz')),
                    ),
                ],
                1: values.RAM,
                2: [
                    values.Disk,
                    ValuePipe(values.Disk, 
                                 [],
                                 ValueMatch(values.Disk, re.compile('(?P<disk_cnt>\d+)x')),
                    ),
                ],
                6: values.Traffic,
                7: [ValueMatch(values.Price, re.compile('(?P<price>\d+\.\d+)')), ValueSet(values.Price, currency_code='EUR', currency_symb='€')],
            }),
            (('body',), {
                0: [
                    ValueSet(values.Virt, vtype='KVM'),
                    # ValueSet(values.Location, loc=['Buffalo, NY', 'Los Angeles, CA', 'Dallas, TX', 'Chicago, IL', 'Seattle, WA', 'Frankfurt, Germany', 'Phoenix, AZ', 'Piscataway, NJ', 'San Jose, CA', 'Atlanta, GA']),
                    # ValueSet(values.DDoS, available=True, desc='New York Only'),
                ]
            }),
        ]),
    ],
}
