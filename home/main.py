from modules.home_manager import Home

credentials = {
    'username': 'self',
    'password': 'password',
    'database': 'smart_home',
    'host': '192.168.50.173'}


def main():
    home = Home('executor', credentials)  # Create Main class
    home.initialize()  # Initialize home
    home.run()  # Run main loop


if __name__ == '__main__':
    main()
