"""Quick script to test the PaymentSimulator idempotency behavior.

Run from the `Backend` directory with a Python venv where `redis` is installed and Redis running.
"""
import pprint
import os
import sys

# Ensure the `Backend` package root is on sys.path when running this script directly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from payments import payment_simulator


def run_demo():
    key = 'demo-idemp-123'
    payment = {'card_number': '4242424242424242'}
    print('First attempt (should charge):')
    r1 = payment_simulator.simulate_charge(1000, payment, key)
    pprint.pprint(r1)

    print('\nSecond attempt with same idempotency key (should return same result):')
    r2 = payment_simulator.simulate_charge(1000, payment, key)
    pprint.pprint(r2)

    print('\nForced failure example:')
    r3 = payment_simulator.simulate_charge(1000, {'force': 'fail'}, 'demo-fail-1')
    pprint.pprint(r3)


if __name__ == '__main__':
    run_demo()
