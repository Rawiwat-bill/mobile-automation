import re
import os
import time

SENSITIVE_KEYS = [
    # auth
    'authorization', 'access_token', 'access-token', 'accessToken',
    'refresh_token', 'refresh-token', 'refreshToken',
    'id_token', 'id-token', 'idToken',
    'token', 'bearer', 'api_key', 'api-key', 'apikey', 'API_KEY',
    # session
    'cookie', 'set-cookie', 'session', 'session_id', 'session-id', 'sessionId',
    # secrets
    'otp', 'pin', 'password', 'passwd', 'secret', 'secret_key', 'private_key',
    # identity
    'citizen_id', 'citizen-id', 'citizenId', 'cid',
    'national_id', 'national-id', 'nationalId',
    'id_card', 'id-card', 'idCard', 'passport',
    # contact
    'mobile', 'mobile_number', 'mobile-number', 'mobileNumber',
    'phone', 'phone_number', 'phone-number', 'telephone', 'email',
    # financial
    'account_no', 'account-no', 'accountNo', 'account_number',
    'account-number', 'accountNumber',
    'card_no', 'card-no', 'cardNo', 'card_number',
    'card-number', 'cardNumber', 'cvv',
    # device
    'device_id', 'device-id', 'deviceId', 'device_token',
    'device-token', 'deviceToken', 'imei',
]


class api_log_redactor:
    def __init__(self):
        self._compile()

    def _compile(self):
        self.rx_bearer = re.compile(r'(?i)(bearer\s+)\S+')
        self.rx_basic = re.compile(r'(?i)(basic\s+)\S+')
        self.rx_json = []
        self.rx_url = []
        self.rx_header = []
        self.all_keys_lower = set(k.lower() for k in SENSITIVE_KEYS)
        for key in SENSITIVE_KEYS:
            k = re.escape(key)
            self.rx_json.append(
                re.compile(rf'("{k}"\s*:\s*)"[^"]*"', re.IGNORECASE)
            )
            self.rx_url.append(
                re.compile(rf'([?&])({k})=([^&\s#]+)', re.IGNORECASE)
            )
            self.rx_header.append(
                re.compile(rf'^(.*:\s*)?({k}):\s+\S.*$', re.IGNORECASE | re.MULTILINE)
            )

    @staticmethod
    def _is_api_line(line):
        hints = [
            'http', 'api', 'request', 'response',
            'okhttp', 'retrofit', 'volley', 'url', 'endpoint',
            'json', 'payload', 'GET ', 'POST ', 'PUT ', 'DELETE ', 'PATCH ',
            'https://', 'http://', 'status', '200', '201', '400', '401',
            '403', '404', '500',
        ]
        lower = line.lower()
        return any(h in lower for h in hints)

    def _redact_line(self, line):
        line = self.rx_bearer.sub(r'\1[REDACTED]', line)
        line = self.rx_basic.sub(r'\1[REDACTED]', line)
        for p in self.rx_json:
            line = p.sub(r'\1"[REDACTED]"', line)
        for p in self.rx_url:
            line = p.sub(r'\1\2=[REDACTED]', line)
        for p in self.rx_header:
            line = p.sub(r'\1\2: [REDACTED]', line)
        return line

    def redact_log(self, raw_path, output_path):
        if not os.path.exists(raw_path):
            return None
        total_lines = 0
        api_lines = 0
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(raw_path, 'r', encoding='utf-8', errors='replace') as infile:
            with open(output_path, 'w', encoding='utf-8') as outfile:
                for line in infile:
                    total_lines += 1
                    if self._is_api_line(line):
                        api_lines += 1
                    redacted = self._redact_line(line)
                    outfile.write(redacted)
        summary = {
            'total_lines': total_lines,
            'api_lines': api_lines,
            'raw_path': raw_path,
            'redacted_path': output_path,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        return summary
