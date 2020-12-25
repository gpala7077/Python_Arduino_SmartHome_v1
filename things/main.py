import sys

from modules.thing_manager import Thing_Main

credentials = {
    'username': 'self',
    'password': 'password',
    'database': 'smart_home',
    'host': '192.168.50.173'}

thing_id = sys.argv[1]


def main():
    thing = Thing_Main(credentials, thing_id)
    thing.initialize()
    thing.run()


if __name__ == '__main__':
    main()