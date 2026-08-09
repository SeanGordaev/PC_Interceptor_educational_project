import json
import socket
from pathlib import Path
from pynput import mouse, keyboard
import threading, queue
import time


class Invader:
    def __init__(self):
        self.Stop = False
        self.conn = None
        self.DataToSend = queue.Queue()
        self.Now = time.monotonic()

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

            while not self.Stop:
                packet = self.DataToSend.get()
                self.SendPacket(packet)

    def SendPacket(self, Packet: bytes) -> None:
        self.conn.sendall(Packet)

    def CreatePacket(self, Data: tuple[bytes, ...]) -> None:
        packet = b""
        for D in Data:
            packet = packet + (len(D).to_bytes(2, "big") + D)
        self.DataToSend.put(packet)

    def SendControlKB(self, key):
        # Mod Control
        mode = "kb".encode()

        # Control
        KeyChat = None
        try:
           KeyChat = key.char.encode()
        except AttributeError:
            KeyChat = str(key).encode()

        # Send Mod and Control
        self.CreatePacket((mode, KeyChat))
        

    def SendMovementMouse(self, x, y):
        # Mod Control
        mode = "pos".encode()
        # Control
        Position = f"{x}|{y}".encode()

        # Send Mod and Control
        self.NewNow = time.monotonic()
        if (self.NewNow - self.Now) > 0.03:
            self.CreatePacket((mode, Position))
            self.Now = self.NewNow
        
    def SendClickMouse(self, x, y, button, pressed):
        if pressed:
            # Mod Control
            mode = "click".encode()
            # Control
            Click = str(button).encode()

            # Send Mod and Control
            self.CreatePacket((mode, Click))

    def GetControl(self):
        listener_mouse = mouse.Listener(
            on_move=self.SendMovementMouse,
            on_click=self.SendClickMouse
        )

        listener_kb = keyboard.Listener(
            on_press=self.SendControlKB
        )

        listener_mouse.start()
        listener_kb.start()

        listener_mouse.join()
        listener_kb.join()

if __name__ == "__main__":
    I = Invader()
