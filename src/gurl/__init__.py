#!/usr/bin/env python
from __future__ import with_statement

import os.path

from _gurl import *

__all__ = ['UrlBuilder', 'Url']

def get_domain(self):
    parts = filter(lambda p: p != '', self.hostname.split('.'))

    for idx in range(len(parts)):
        domain = '.'.join(parts[idx:])

        value = Url.tld_domains.get(domain, None)

        if value is None:
            continue

        exception, wildcard = value

        if exception:
            return domain

        if wildcard:
            return '.'.join(parts[idx-2:])

        return '.'.join(parts[idx-1:])

Url.domain = property(get_domain)

def load_tld_domains():
    tld_domains = {}
    
    with open(os.path.join(os.path.dirname(__file__), 'effective_tld_names.dat'), 'r') as f:
        for line in f:
            line = line.strip()

            if line.startswith('//') or line == '': continue

            exception = False
            wildcard = False

            if line[0] == '!':
                domain = line[1:]
                exception = True
            elif line[0] == '*':
                domain = line[2:]
                wildcard = True
            else:
                domain = line

            tld_domains[domain] = (exception, wildcard)

    return tld_domains

Url.tld_domains = load_tld_domains()