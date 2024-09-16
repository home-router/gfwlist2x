#!/usr/bin/python3

"""
Convert gfwlist to various formats.

# AdguardHome

Run with:

```bash
gfwlist2x.py -d -g gfwlist.txt -o adg.txt -f adguardhome
```

In AdguardHome config file, add the following confie:

```
upstream_dns_file: /path/to/adg.txt
```
"""

import base64
from pathlib import Path
import re
import traceback
import urllib.request

# Aliyun DNS
AliYun_DNS_SERVER = [
    '223.5.5.5',
    '223.6.6.6',
    '2400:3200::1',
    '2400:3200:baba::1',
]

BASE_DNS_SERVER = AliYun_DNS_SERVER

# Use Google public DNS because it support ECS.
DEFAULT_SECURE_DNS_SERVER = '8.8.8.8'


class GfwList:
    URLs = [
        'https://pagure.io/gfwlist/raw/master/f/gfwlist.txt',
        'http://repo.or.cz/gfwlist.git/blob_plain/HEAD:/gfwlist.txt',
        'https://bitbucket.org/gfwlist/gfwlist/raw/HEAD/gfwlist.txt',
        'https://gitlab.com/gfwlist/gfwlist/raw/master/gfwlist.txt',
        'https://git.tuxfamily.org/gfwlist/gfwlist.git/plain/gfwlist.txt',
        'https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt',
    ]

    def __init__(self, dns_server: str):
        """
        :param dns_server: dns server to use for resolving domains in gfwlist
        """
        self.domains = set()
        self.dns_server = dns_server

    @staticmethod
    def _fetch_url(url):
        try:
            print(f'downloding gfwlist from {url}')
            with urllib.request.urlopen(url) as response:
                data = response.read()
            return data
        except:
            print(f'download {url} failed')
            traceback.print_exc()
            return None

    def fetch(self):
        for url in self.URLs:
            data = self._fetch_url(url)
            if data:
                return data
        print(f'fail to download gfwlist')

    # Refer to https://github.com/cokebar/gfwlist2dnsmasq/blob/master/gfwlist2dnsmasq.sh
    # for a bash implementation which parses gfwlist and generates dnsmasq config.
    # This parser is based on the bash implementation.

    # Ignore
    # 1. comments starting with '!'
    # 2. white list starting with @@
    # 3. urls with IPv4 address
    ignore_pattern = re.compile(r'^\!|\[|^@@|(https?://){0,1}[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')

    # Remove:
    # 1. starting || or |
    # 2. url protocol (http:// or https://)
    head_filter_pattern = re.compile(r'^(\|\|?)?(https?://)?')

    # Remove the path and query string from URL.
    tail_filter_pattern = re.compile(r'/.*$|%2F.*$')

    domain_pattern = re.compile(r'([a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)')
    wildcard_pattern = re.compile(r'^(([a-zA-Z0-9]*\*[-a-zA-Z0-9]*)?(\.))?([a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)(\*[a-zA-Z0-9]*)?$')

    def _parse_line(self, line):
        is_regex_rule = False
        origin_line = line
        if line.startswith('/'):
            is_regex_rule = True

        # Ignore comments.
        if self.ignore_pattern.search(line):
            if is_regex_rule:
                print(f'please add domain manually for ignored regex rule: {origin_line}')
            return

        line = self.head_filter_pattern.sub('', line)
        line = self.tail_filter_pattern.sub('', line)

        if not self.domain_pattern.search(line):
            if is_regex_rule:
                print(f'please add domain manually for ignored regex rule: {origin_line}')
            return

        domain = self.wildcard_pattern.search(line).groups()[3]
        if is_regex_rule:
            print(f'regex rule {line} -> {domain}')
        self.domains.add(domain)

    def parse(self, data):
        """
        Return False if there are parsing errors.
        """
        lines = data.splitlines()
        if len(lines) == 0:
            print('gfwlist is empty')
            return False

        if not lines[0].startswith('[AutoProxy'):
            print('gfwlist is not in AutoProxy format')
            return False

        for line in lines[0:]:
            # Parse gfwlist line by line.
            # Add each domain to self.domains.
            self._parse_line(line)

    def add_extra_domains(self):
        print('adding google domains')
        self.domains.update(['google.com', 'google.ad', 'google.ae',
        'google.com.af', 'google.com.ag', 'google.com.ai', 'google.al',
        'google.am', 'google.co.ao', 'google.com.ar', 'google.as', 'google.at',
        'google.com.au', 'google.az', 'google.ba', 'google.com.bd', 'google.be',
        'google.bf', 'google.bg', 'google.com.bh', 'google.bi', 'google.bj',
        'google.com.bn', 'google.com.bo', 'google.com.br', 'google.bs',
        'google.bt', 'google.co.bw', 'google.by', 'google.com.bz', 'google.ca',
        'google.cd', 'google.cf', 'google.cg', 'google.ch', 'google.ci',
        'google.co.ck', 'google.cl', 'google.cm', 'google.cn', 'google.com.co',
        'google.co.cr', 'google.com.cu', 'google.cv', 'google.com.cy',
        'google.cz', 'google.de', 'google.dj', 'google.dk', 'google.dm',
        'google.com.do', 'google.dz', 'google.com.ec', 'google.ee',
        'google.com.eg', 'google.es', 'google.com.et', 'google.fi',
        'google.com.fj', 'google.fm', 'google.fr', 'google.ga', 'google.ge',
        'google.gg', 'google.com.gh', 'google.com.gi', 'google.gl', 'google.gm',
        'google.gp', 'google.gr', 'google.com.gt', 'google.gy', 'google.com.hk',
        'google.hn', 'google.hr', 'google.ht', 'google.hu', 'google.co.id',
        'google.ie', 'google.co.il', 'google.im', 'google.co.in', 'google.iq',
        'google.is', 'google.it', 'google.je', 'google.com.jm', 'google.jo',
        'google.co.jp', 'google.co.ke', 'google.com.kh', 'google.ki',
        'google.kg', 'google.co.kr', 'google.com.kw', 'google.kz', 'google.la',
        'google.com.lb', 'google.li', 'google.lk', 'google.co.ls', 'google.lt',
        'google.lu', 'google.lv', 'google.com.ly', 'google.co.ma', 'google.md',
        'google.me', 'google.mg', 'google.mk', 'google.ml', 'google.com.mm',
        'google.mn', 'google.ms', 'google.com.mt', 'google.mu', 'google.mv',
        'google.mw', 'google.com.mx', 'google.com.my', 'google.co.mz',
        'google.com.na', 'google.com.nf', 'google.com.ng', 'google.com.ni',
        'google.ne', 'google.nl', 'google.no', 'google.com.np', 'google.nr',
        'google.nu', 'google.co.nz', 'google.com.om', 'google.com.pa',
        'google.com.pe', 'google.com.pg', 'google.com.ph', 'google.com.pk',
        'google.pl', 'google.pn', 'google.com.pr', 'google.ps', 'google.pt',
        'google.com.py', 'google.com.qa', 'google.ro', 'google.ru', 'google.rw',
        'google.com.sa', 'google.com.sb', 'google.sc', 'google.se',
        'google.com.sg', 'google.sh', 'google.si', 'google.sk', 'google.com.sl',
        'google.sn', 'google.so', 'google.sm', 'google.sr', 'google.st',
        'google.com.sv', 'google.td', 'google.tg', 'google.co.th',
        'google.com.tj', 'google.tk', 'google.tl', 'google.tm', 'google.tn',
        'google.to', 'google.com.tr', 'google.tt', 'google.com.tw',
        'google.co.tz', 'google.com.ua', 'google.co.ug', 'google.co.uk',
        'google.com.uy', 'google.co.uz', 'google.com.vc', 'google.co.ve',
        'google.vg', 'google.co.vi', 'google.com.vn', 'google.vu', 'google.ws',
        'google.rs', 'google.co.za', 'google.co.zm', 'google.co.zw',
        'google.cat'])

        print('add blogspot domains')
        self.domains.update(['blogspot.ca', 'blogspot.co.uk', 'blogspot.com',
        'blogspot.com.ar', 'blogspot.com.au', 'blogspot.com.br',
        'blogspot.com.by', 'blogspot.com.co', 'blogspot.com.cy',
        'blogspot.com.ee', 'blogspot.com.eg', 'blogspot.com.es',
        'blogspot.com.mt', 'blogspot.com.ng', 'blogspot.com.tr',
        'blogspot.com.uy', 'blogspot.de', 'blogspot.gr', 'blogspot.in',
        'blogspot.mx', 'blogspot.ch', 'blogspot.fr', 'blogspot.ie',
        'blogspot.it', 'blogspot.pt', 'blogspot.ro', 'blogspot.sg',
        'blogspot.be', 'blogspot.no', 'blogspot.se', 'blogspot.jp',
        'blogspot.in', 'blogspot.ae', 'blogspot.al', 'blogspot.am',
        'blogspot.ba', 'blogspot.bg', 'blogspot.ch', 'blogspot.cl',
        'blogspot.cz', 'blogspot.dk', 'blogspot.fi', 'blogspot.gr',
        'blogspot.hk', 'blogspot.hr', 'blogspot.hu', 'blogspot.ie',
        'blogspot.is', 'blogspot.kr', 'blogspot.li', 'blogspot.lt',
        'blogspot.lu', 'blogspot.md', 'blogspot.mk', 'blogspot.my',
        'blogspot.nl', 'blogspot.no', 'blogspot.pe', 'blogspot.qa',
        'blogspot.ro', 'blogspot.ru', 'blogspot.se', 'blogspot.sg',
        'blogspot.si', 'blogspot.sk', 'blogspot.sn', 'blogspot.tw',
        'blogspot.ug', 'blogspot.cat'])

        print('add twimg.edgesuite.net')
        self.domains.add('twimg.edgesuite.net')

    def format_adguardhome(self, output):
        with open(output, 'w') as f:
            for server in BASE_DNS_SERVER:
                f.write(f'{server}\n')
            for domain in self.domains:
                f.write(f'[/{domain}/]{self.dns_server}\n')

            extra = Path('./extra.txt')
            if extra.exists():
                with open(extra, 'r') as ex:
                    f.write(ex.read())


    def format_raw(self, output):
        with open(output, 'w') as f:
            for domain in self.domains:
                f.write(f'{domain}\n')

    def run(self, output: str, download: bool, gfwlist_fname: str, format: str):
        """
        :param download: download gfwlist from internet
        :param gfwlist: save downloaded gfwlist to this file
        :param output: save output to this file
        """
        if download:
            data = self.fetch()
            data = base64.b64decode(data).decode('utf-8')
        elif gfwlist_fname:
            data = open(gfwlist_fname, 'r').read()
        else:
            print(f'either download or gfwlist_fname must be specified')
            return

        if download and gfwlist_fname:
            with open(gfwlist_fname, 'w') as f:
                f.write(data)

        self.parse(data)
        self.add_extra_domains()

        if format == 'raw':
            self.format_raw(output)
        elif format == 'adguardhome':
            self.format_adguardhome(output)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate dnsmasq config from gfwlist.')
    parser.add_argument('-d', '--download', action='store_true', help='download gfwlist from internet')
    parser.add_argument('-g', '--gfwlist', type=str, help='save downloaded gfwlist to this file')
    parser.add_argument('-o', '--output', type=str, help='save output to this file', required=True)
    parser.add_argument('-s', '--dns-server', type=str, help='dns server to use for resolving domains in gfwlist', 
                        default=DEFAULT_SECURE_DNS_SERVER)
    parser.add_argument('-f', '--format', type=str, help='format of output file', default='raw')
    args = parser.parse_args()

    gfwlist = GfwList(args.dns_server)
    gfwlist.run(args.output, args.download, gfwlist_fname=args.gfwlist, format=args.format)

