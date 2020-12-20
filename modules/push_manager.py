import requests
import json


class Push:
    def __init__(self, key):
        self.key = key

    def send(self, api_call, title=None, body=None, numbers=None):
        api = {

            'push': {
                'base': 'https://api.pushbullet.com/v2/pushes',
                'data': {"type": "note", "title": title, "body": body}},

            'devices': {
                'base': 'https://api.pushbullet.com/v2/texts',
                'data': {"data": {"addresses": numbers, "message": body}}}
        }
        resp = requests.post(api[api_call]['base'],
                             data=json.dumps(api[api_call]['data']),
                             headers={'Authorization': 'Bearer ' + self.key,
                                      'Content-Type': 'application/json'})
        if resp.status_code != 200:
            raise Exception('Error', resp.status_code)
        else:
            return resp


if __name__ == '__main__':
    push = Push(key='o.6uxjgUM6ci0mNODdvolcqXtGOMUFLfOG')
    print(push.send('push', body='hello').text)


