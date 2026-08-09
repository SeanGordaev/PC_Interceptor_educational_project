import json
import socket
from pathlib import Path
from pynput import mouse, keyboard
import threading


class Invader:
    def __init__(self):
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

            Detect = threading.Thread(target=self.GetControl)
            Detect.start()

    def SendControlKB(self, key):
        # Send The Mod Control
        mode = "kb".encode()
        self.conn.sendall(len(mode).to_bytes(1, "big"))

        # Send The Control
        try:
           KeyChat = key.char.encode()
           self.conn.sendall(len(KeyChat).to_bytes(2, "big") + KeyChat)
        except AttributeError:
            SpKeyChat = str(key).encode()
            self.conn.sendall(len(SpKeyChat).to_bytes(2, "big") + SpKeyChat)

    def SendMovementMouse(self, x, y):
        # Send The Mod Control
        mode = "pos".encode()
        self.conn.sendall(len(mode).to_bytes(1, "big"))

        # Send The Control
        Position = f"{x}|{y}".encode()
        self.conn.sendall(len(Position).to_bytes(2, "big") + Position)
        
    def SendClickMouse(self, x, y, button, pressed):
        # Send The Mod Control
        mode = "click".encode()
        self.conn.sendall(len(mode).to_bytes(1, "big"))

        # Send The Control
        if pressed:
            Click = str(button).encode()
            self.conn.sendall(len(Click).to_bytes(2, "big") + Click)

    def GetControl(self):
        with keyboard.Listener(on_press=self.SendControlKB) as listener_kb, \
            mouse.Listener(on_move=self.SendMovementMouse, on_click=self.SendClickMouse) as listener_mouse:
            listener_mouse.join()
            listener_kb.join()

if __name__ == "__main__":
    I = Invader()
