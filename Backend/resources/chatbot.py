import os
from flask_restful import Resource
from flask import request
import logging


class ChatbotResource(Resource):
    """Simple chatbot endpoint. If OPENAI_API_KEY is configured, proxy to OpenAI's Chat API.
    Otherwise use a small rule-based fallback for common support questions.
    """

    def post(self):
        data = request.get_json() or {}
        msg = data.get('message', '')

        if not msg:
            return {'message': 'No message provided'}, 400

        openai_key = os.environ.get('OPENAI_API_KEY')
        if openai_key:
            try:
                # import requests lazily so missing optional dependency doesn't break startup
                try:
                    import requests
                except Exception:
                    logging.warning('`requests` not installed; falling back to rule-based chatbot')
                    requests = None

                if requests:
                    headers = {
                        'Authorization': f'Bearer {openai_key}',
                        'Content-Type': 'application/json'
                    }
                    payload = {
                        'model': 'gpt-4o-mini',
                        'messages': [
                            {'role': 'system', 'content': 'You are a friendly support assistant for TicketShow.'},
                            {'role': 'user', 'content': msg}
                        ],
                        'max_tokens': 300
                    }
                    resp = requests.post('https://api.openai.com/v1/chat/completions', json=payload, headers=headers, timeout=10)
                    resp.raise_for_status()
                    data = resp.json()
                    # Extract assistant reply
                    reply = ''
                    try:
                        reply = data['choices'][0]['message']['content']
                    except Exception:
                        reply = data.get('choices', [{}])[0].get('text', '')

                    return {'reply': reply}
            except Exception as e:
                logging.warning(f'OpenAI proxy failed: {e}')
                # Fall back to rules if OpenAI fails
                pass

        # Rule-based fallback
        lower = msg.lower()
        if 'refund' in lower or 'cancel' in lower:
            return {'reply': 'To request a refund or cancel a booking, please visit your dashboard -> bookings and choose cancel. If you need help, email support@yourdomain.com.'}
        if 'how' in lower and 'book' in lower:
            return {'reply': 'Select a show, pick available seats and complete payment. Use the cart to review before confirming.'}
        if 'support' in lower or 'help' in lower:
            return {'reply': 'You can reach support at support@yourdomain.com. Provide your booking id and we will help.'}

        # Generic reply
        return {'reply': "I'm here to help — please describe your issue and include booking id if available."}
