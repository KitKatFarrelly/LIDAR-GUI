import os
import sys
import tkinter as tk
import serial
from serial.tools import list_ports

class MainGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LIDAR GUI")
        self.geometry("1200x720")


if __name__ == "__main__":
    app = MainGui()
    app.mainloop()
