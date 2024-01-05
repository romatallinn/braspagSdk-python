import json
import uuid

from future.utils import raise_with_traceback
from requests import Request, Session


class Base(object):

    def __init__(self, authorization_headers):
        self.authorization_headers = authorization_headers

    def send_request(self, method, uri, data=None, params=None):

        s = Session()

        body = data

        headers = {
            'User-Agent': "BraspagSdk/Python",
            'RequestId': str(uuid.uuid4()),
            **(self.authorization_headers or {}),
        }

        if not body:
            headers['Content-Length'] = '0'
        else:
            headers["Content-Type"] = "application/json"

            if not isinstance(data, dict):
                body = body.toJSON()

        req = Request(method, uri, data=body, headers=headers, params=params)

        prep = s.prepare_request(req)

        response = s.send(prep)

        if 'json' in response.headers['Content-Type'].lower():
            answers = response.json()
        else:
            answers = [{
                'Code': str(response.status_code),
                'Message': response.text
            }]

        if response.status_code >= 400:
            errors = []

            for answer in answers:
                errors.append('\r\n * [%s] %s\r\n' % (answer['Code'], answer['Message']))

            data_send = json.loads(body or 'null')

            raise_with_traceback(Exception('\r\n%s\r\nMethod: %s\r\nUri: %s\r\nData: %s' % (''.join(errors), method, response.url, json.dumps(data_send, indent=2))))

        return answers


class ApiBase(Base):

    def __init__(self, credentials):
        authorization_headers = {
            'MerchantId': credentials.merchant_id,
            'MerchantKey': credentials.merchant_key,
        }
        super().__init__(authorization_headers=authorization_headers)


class ApiOauthBase(Base):

    def __init__(self, access_token):
        authorization_headers = {
            'Authorization': 'Bearer ' + access_token,
        }
        super().__init__(authorization_headers=authorization_headers)
