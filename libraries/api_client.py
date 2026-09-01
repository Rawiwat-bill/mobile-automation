import json
import requests

class ApiClient:
    def send_api(self, method, url, payload=None):
        method = str(method).upper().strip()
        headers = {"Content-Type": "application/json"}

        json_data = None
        data = None

        if payload is not None and str(payload).strip() != "":
            raw = str(payload).strip()
            try:
                json_data = json.loads(raw)
            except Exception:
                data = raw

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=json_data,
            data=data,
            timeout=30,
            verify=False
        )

        try:
            body_text = json.dumps(response.json(), ensure_ascii=False)
        except Exception:
            body_text = response.text

        return response.status_code, body_text

    