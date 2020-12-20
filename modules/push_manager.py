from pushbullet import Listener, Pushbullet


class Push:
    def __init__(self, key):
        self.key = key
        self.push = Pushbullet(key)
        self.commands = None

    def on_push(self, data):
        print("Received data:\n{}".format(data))
        latest_push = self.push.get_pushes()[0]
        if 'title' not in latest_push:
            self.push.push_note('SmartHome Commands', self.commands.execute(latest_push['body']))

    def listen(self):
        s = Listener(account=self.push, on_push=self.on_push, http_proxy_host=None, http_proxy_port=None)
        try:
            s.run_forever()
        except KeyboardInterrupt:
            s.close()

    def delete_pushes(self):
        return self.push.delete_pushes()


if __name__ == '__main__':
    push = Push('o.aFYUBKPv0sDSwAcFJXkcHj0rYYRCFWZa')
