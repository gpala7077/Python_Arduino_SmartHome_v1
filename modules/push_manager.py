from pushbullet import Listener, Pushbullet


class Push:
    def __init__(self, key):
        self.key = key
        self.push = Pushbullet(key)
        self.commands = None

    def listen(self, on_push=None):
        s = Listener(account=self.push, on_push=on_push, http_proxy_host=None, http_proxy_port=None)
        try:
            s.run_forever()
        except KeyboardInterrupt:
            s.close()

    def clear_pushes(self):
        return self.push.delete_pushes()


if __name__ == '__main__':
    push = Push('o.aFYUBKPv0sDSwAcFJXkcHj0rYYRCFWZa')
