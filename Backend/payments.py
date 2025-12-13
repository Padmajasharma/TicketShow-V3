"""Payment simulator for testing workflows without a real gateway.

Features:
- Simulate success/failure based on `payment_method` fields (card number parity).
- Idempotency storage in Redis keyed by `payment:idempotency:{key}` to avoid double-charging.
"""
import os
import json
import logging
from typing import Dict, Optional

import redis

logger = logging.getLogger(__name__)


class PaymentSimulator:
    def __init__(self, redis_url: Optional[str] = None):
        # Connect to Redis used by the app (accept REDIS_URL env var)
        try:
            if redis_url:
                self.redis = redis.from_url(redis_url, decode_responses=True)
            else:
                # honor REDIS_URL env if set, otherwise default host
                self.redis = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'), decode_responses=True)
        except Exception:
            # fall back to a local client that will raise on use
            self.redis = None

    def _idempotency_key(self, key: str) -> str:
        return f"payment:idempotency:{key}"

    def get_idempotency(self, key: str) -> Optional[Dict]:
        if not key or not self.redis:
            return None
        try:
            data = self.redis.get(self._idempotency_key(key))
            return json.loads(data) if data else None
        except Exception as e:
            logger.warning(f"Failed to read idempotency {key}: {e}")
            return None

    def record_idempotency(self, key: str, result: Dict) -> None:
        if not key or not self.redis:
            return
        try:
            self.redis.set(self._idempotency_key(key), json.dumps(result), ex=60 * 60 * 24)
        except Exception as e:
            logger.warning(f"Failed to write idempotency {key}: {e}")

    def simulate_charge(self, amount_cents: int, payment_method: Dict, idempotency_key: Optional[str] = None) -> Dict:
        """Simulate a payment charge.

        Simple deterministic rule:
        - If `payment_method['card_number']` exists and ends with an even digit -> success.
        - If it ends with an odd digit -> failure.
        - If `payment_method` contains `force: 'fail'` or `force: 'success'`, honor that.

        Returns a dict: {status: 'success'|'failure', transaction_id, reason}
        """
        # Idempotency short-circuit
        if idempotency_key:
            prev = self.get_idempotency(idempotency_key)
            if prev:
                return prev

        # Evaluate forced flags first
        try:
            if payment_method and isinstance(payment_method, dict):
                forced = payment_method.get('force')
                if forced == 'success':
                    result = {'status': 'success', 'transaction_id': f"sim-{os.urandom(6).hex()}", 'reason': 'forced_success'}
                    if idempotency_key:
                        self.record_idempotency(idempotency_key, result)
                    return result
                if forced == 'fail':
                    result = {'status': 'failure', 'transaction_id': None, 'reason': 'forced_failure'}
                    if idempotency_key:
                        self.record_idempotency(idempotency_key, result)
                    return result

                card = payment_method.get('card_number')
                if card and isinstance(card, str) and card.isdigit():
                    last = int(card[-1])
                    if last % 2 == 0:
                        result = {'status': 'success', 'transaction_id': f"sim-{os.urandom(6).hex()}", 'reason': 'even_card_success'}
                        if idempotency_key:
                            self.record_idempotency(idempotency_key, result)
                        return result
                    else:
                        result = {'status': 'failure', 'transaction_id': None, 'reason': 'odd_card_failure'}
                        if idempotency_key:
                            self.record_idempotency(idempotency_key, result)
                        return result

        except Exception as e:
            logger.warning(f"Payment simulation error: {e}")

        # Default: success
        result = {'status': 'success', 'transaction_id': f"sim-{os.urandom(6).hex()}", 'reason': 'default_success'}
        if idempotency_key:
            self.record_idempotency(idempotency_key, result)
        return result


# singleton instance for convenience
payment_simulator = PaymentSimulator()
