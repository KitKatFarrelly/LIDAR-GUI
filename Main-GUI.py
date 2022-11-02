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
        self.buttonfont = "Helvetica 16"
        self.dropdownfont = "Helvetica 12"
        self.ser = serial.Serial()
        self.port_options = []
        self.optionvar = tk.StringVar()
        self.serial_ports()
        self.gui_elements()
        self.update_display()
        self.init_finished = True


    def serial_ports(self):
        self.port_options = []
        for port in serial.tools.list_ports.comports():
            self.port_options.append(port.device)
        if(self.init_finished):
            self.portmenu['values'] = self.port_options

        if(self.ser.is_open):
            port_flag = False
            for port in serial.tools.list_ports.comports():
                if(str(self.ser.port) == str(port.device)):
                    port_flag = True
            if(not port_flag):
                self.ser.close()

    def serial_connect(self):
        if(not self.ser.is_open):
            self.ser.port = str(self.optionvar.get())
            self.ser.baud = 115200
            self.ser.open()
        else:
            self.ser.close()

    def gui_elements(self):

        #com port selection
        self.portmenu = ttk.Combobox(self, font = self.dropdownfont, textvariable = self.optionvar)
        self.portmenu.set(self.port_options[0])
        self.portmenu['values'] = self.port_options
        self.portmenu.grid(column=0, row=0)

        #connects to selected com port
        self.connectbutton = tk.Button(self, font = self.buttonfont)
        self.connectbutton["text"] = "Connect"
        self.connectbutton["bg"] = "red"
        self.connectbutton["command"] = self.serial_connect
        self.connectbutton.grid(column=1,row=0)

        self.cmd_line = tk.Listbox(self, bg = 'black', fg = 'white', height = 395, width = 1195, highlightthickness = 0, selectbackground = 'black', activestyle = tk.NONE)
        self.cmd_line.place(x = 0, y = 320)

    def command_line(self):
        if(self.ser.is_open and self.ser._port_handle):
            while(self.ser.in_waiting):
                serial_line = self.ser.read(self.ser.in_waiting).decode('utf-8')
                print(serial_line)
                #self.cmd_line.insert(tk.END, serial_line)
                #if(self.cmd_line.size() > 25):
                    #self.cmd_line.delete(0)

    def update_display(self):
        if(self.ser.is_open):
            self.connectbutton["bg"] = "green"
        else:
            self.connectbutton["bg"] = "red"
        self.serial_ports()
        self.command_line()
        self.after(100, self.update_display)


if __name__ == "__main__":
    app = MainGui()
    app.mainloop()
