import requests
import json

import ssl
import asyncio
import websockets


class Push:
    def __init__(self, key):
        self.key = key

    def send(self, api_call, title=None, body=None, numbers=None):
        api = {

            'push': {
                'base': 'https://api.pushbullet.com/v2/pushes',
                'data': {"type": "note", "title": title, "body": body}},

            'text': {
                'base': 'https://api.pushbullet.com/v2/texts',
                'data': {"data": {"addresses": numbers, "message": body, "target_device_iden": "uju1rIlCOPIsjvhLqu6d0S"}}}
        }
        resp = requests.post(api[api_call]['base'],
                             data=json.dumps(api[api_call]['data']),
                             headers={'Authorization': 'Bearer ' + self.key,
                                      'Content-Type': 'application/json'})
        if resp.status_code != 200:
            raise Exception('Error', resp.status_code)
        else:
            return resp

    def get(self, api_call):
        api = {
            'devices': {
                'base': 'https://api.pushbullet.com/v2/devices',
                'data': {"data": {"addresses": None, "message": 'body'}}
            }
        }

        resp = requests.post(api[api_call]['base'],
                             data=json.dumps(api[api_call]['data']),
                             headers={'Authorization': 'Bearer ' + self.key,
                                      'Content-Type': 'application/json'})
        if resp.status_code != 200:
            raise Exception('Error', resp.status_code)
        else:
            return resp

