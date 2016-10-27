#!/usr/bin/python
'''
Script to test threading functions on archive.
'''
# Set PYTHONPATH and load environment variables for standalone script -----------------
# for file living in project/bin/
import os
import sys


path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if not path in sys.path:
    sys.path.insert(0, path)

if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mlarchive.settings.laptop'

virtualenv_activation = os.path.join(path, "bin", "activate_this.py")
if os.path.exists(virtualenv_activation):
    execfile(virtualenv_activation, dict(__file__=virtualenv_activation))

import django
django.setup()

# -------------------------------------------------------------------------------------
import argparse
import time

from mlarchive.archive.models import Message, EmailList
from mlarchive.archive.thread import process

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print '%r (%r, %r) %2.2f sec' % \
              (method.__name__, args, kw, te-ts)
        return result

    return timed

@timeit
def do_thread(elist, args):
    queryset = Message.objects.filter(email_list=elist).order_by('date')
    # DEBUG
    #ids = ['55ADF8D7.1000608@meinberg.de', '613F85B8-20E2-45AB-A1D9-1CACC5B82F64@noao.edu']
    #queryset = Message.objects.filter(email_list__name='ntp',subject__contains='Proposed REFID changes').order_by('date')
    #queryset = Message.objects.filter(email_list__name='ntp',msgid__in=ids).order_by('date')
    process(queryset, debug=args.verbose)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
    parser.add_argument('-s', '--start', help='the list to start with')
    parser.add_argument('-l', '--list', help='the list to process')
    args = parser.parse_args()
    kwargs = {}
    if args.list:
        kwargs['name'] = args.list
    if args.start:
        kwargs['name__gte'] = args.start

    elists = EmailList.objects.filter(**kwargs).order_by('name')
    for elist in elists:
        do_thread(elist, args)


if __name__ == "__main__":
    main()