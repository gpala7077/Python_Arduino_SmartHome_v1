from modules.thing_manager import MCU, load_data


if __name__ == '__main__':
    info = load_data()
    MCU = MCU(info['data'], info['query'])
