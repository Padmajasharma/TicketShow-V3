#!/usr/bin/env python3
"""Call the analytics endpoint using Flask test client and print results.

Run from the `Backend` folder:
    python3 scripts/show_analytics.py
"""
import json
import os
import sys

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from run import app


def pretty_print(title, resp):
    print('\n' + '='*40)
    print(title)
    print('='*40)
    try:
        data = resp.get_json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception:
        print('Non-JSON response:')
        print(resp.data.decode())


def main():
    with app.test_client() as c:
        # 1) Default: last 30 days (frontend default)
        r1 = c.get('/analytics/sales')
        pretty_print('Default (last 30 days)', r1)

        # 2) All-time, include unconfirmed
        r2 = c.get('/analytics/sales?group_by=movie&since_days=0&include_unconfirmed=1')
        pretty_print('All-time (include unconfirmed)', r2)

        # 3) All-time, only confirmed
        r3 = c.get('/analytics/sales?group_by=movie&since_days=0')
        pretty_print('All-time (confirmed only)', r3)


if __name__ == '__main__':
    main()
