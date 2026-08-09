"""Invader server: collect local input and send control packets over TCP."""

import socket
from pynput import mouse, keyboard
from pynput.mouse import Controller as Controller_mouse
import threading, queue
import time


class Invader:
    def __init__(self):
        self.Stop = False
        self.Start = True
        self.conn = None
        self.DataToSend = queue.Queue()
        self.Control_m = Controller_mouse()
        self.Now = time.monotonic()

        HOST = "IP-ADDRESS-INVADER"
        PORT = "PORT-INVADER"

        # Start the server socket, accept one client, and begin capturing input.
        # Keyboard and mouse events are queued and sent from the main loop.
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
        """Send a complete packet to the connected client."""
        self.conn.sendall(Packet)

    def CreatePacket(self, Data: tuple[bytes, ...]) -> None:
        """Build a length-prefixed packet from multiple data parts."""
        packet = b""
        for D in Data:
            print(D.decode())
            packet = packet + (len(D).to_bytes(2, "big") + D)
        self.DataToSend.put(packet)

    def SendControlKB(self, key):
        # Packet mode: keyboard input.
        mode = "kb".encode()

        # Stop on ESC, otherwise send the pressed key.
        if key == keyboard.Key.esc:
            self.Stop = True
            return
        KeyChat = None
        try:
           KeyChat = key.char.encode()
        except AttributeError:
            KeyChat = str(key).encode()

        # Send Mod and Control
        self.CreatePacket((mode, KeyChat))
        

    def SendMovementMouse(self, x, y):
        if self.Start:
            self.Control_m.position = (0, 0)
            self.Start = False

        # Packet mode: mouse position update.
        mode = "pos".encode()
        # Control payload: current cursor coordinates.
        Position = f"{x}|{y}".encode()

        # Throttle updates so the client does not receive too many packets.
        self.NewNow = time.monotonic()
        if (self.NewNow - self.Now) > 0.03:
            self.CreatePacket((mode, Position))
            self.Now = self.NewNow
        
    def SendClickMouse(self, x, y, button, pressed):
        if pressed:
            # Packet mode: mouse click event.
            mode = "click".encode()
            # Control payload: clicked button name.
            Click = str(button).encode()

            # Send click event to the client.
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
