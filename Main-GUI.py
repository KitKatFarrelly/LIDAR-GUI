import os
import sys
import tkinter as tk
from tkinter import ttk
import serial
from serial.tools import list_ports

class MainGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LIDAR GUI")
        self.geometry("1200x720")
        self.init_finished = False
        self.buttonfont = "Helvetica 24"
        self.dropdownfont = "Helvetica 12"
        self.ser = serial.Serial()
        self.port_options = []
        self.optionvar = tk.StringVar()
        self.serial_ports()
        self.gui_elements()
        self.init_finished = True


    def serial_ports(self):
        self.port_options = []
        for port in serial.tools.list_ports.comports():
            self.port_options.append(port.device)
        if(self.init_finished):
            self.portmenu.set(self.port_options[0])
            self.portmenu['values'] = self.port_options

    def serial_connect(self):
        self.ser.port = str(self.optionvar.get())
        self.ser.baud = 115200
        self.ser.open()
        self.connectbutton["bg"] = "green"

    def gui_elements(self):

        #com port selection
        self.portmenu = ttk.Combobox(self, font = self.dropdownfont, textvariable = self.optionvar)
        self.portmenu.set(self.port_options[0])
        self.portmenu['values'] = self.port_options
        self.portmenu.grid(column=0, row=0)

        #refreshes com port options
        self.refresh = tk.Button(self, font = self.buttonfont)
        self.refresh["text"] = "Refresh"
        self.refresh["command"] = self.serial_ports
        self.refresh.grid(column=0,row=1)

        #connects to selected com port
        self.connectbutton = tk.Button(self, font = self.buttonfont)
        self.connectbutton["text"] = "Connect"
        self.connectbutton["bg"] = "red"
        self.connectbutton["command"] = self.serial_connect
        self.connectbutton.grid(column=1,row=0)

    def command_line(self):
        pass

    def update_display(self):
        pass


if __name__ == "__main__":
    app = MainGui()
    app.mainloop()
