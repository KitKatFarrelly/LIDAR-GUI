import os
import sys
import re
import codecs
import time
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
        self.serial_line = b''
        self.serial_list = []
        self.serialcommand= tk.StringVar()
        self.ser = serial.serial_for_url('COM3', 115200, do_not_open = True)
        self.port_options = []
        self.optionvar = tk.StringVar()
        self.serial_ports()
        self.gui_elements()
        self.image_line = 0
        self.depth_image = []
        self.depth_match_pattern = re.compile(b'.*,.*,.*,.*,.*,.*,.*,.*,.*')
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
            self.ser.rts = True  # Force an RTS reset on open
            self.ser.open()
            time.sleep(0.005)  # Add a delay to meet the requirements of minimal EN low time (2ms for ESP32-C3)
            self.ser.rts = False
            self.ser.dtr = self.ser.dtr   # usbser.sys workaround
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

        #console output
        self.cmd_line = tk.Listbox(self, bg = 'black', fg = 'white', height = 395, width = 1195, highlightthickness = 0, selectbackground = 'black', activestyle = tk.NONE)
        self.cmd_line.place(x = 0, y = 320)

        #serial write box and enter button
        self.serialwritebox = tk.Entry(self, font = self.buttonfont, textvariable = self.serialcommand)
        self.serialwritebox.grid(column=0,row=1)

        self.serialsend = tk.Button(self, font = self.buttonfont)
        self.serialsend["text"] = "Send"
        self.serialsend["command"] = self.serial_write
        self.serialsend.grid(column=1,row=1)

    def serial_write(self):
        cmd = self.serialcommand.get()
        if(cmd != ""):
            cmd = cmd + '\n'
            bytescmd = bytes(cmd, 'utf-8')
            self.serialcommand.set("")
            if(self.ser.is_open and self.ser._port_handle):
                    self.ser.write(bytescmd)

    def serial_read(self):
        if(self.ser.is_open and self.ser._port_handle):
            if(self.ser.in_waiting):
                try:
                    self.serial_line = self.serial_line + self.ser.read(self.ser.in_waiting)
                    self.serial_list = re.split(rb'(?<=\n)', self.serial_line)
                except serial.SerialException:
                    pass

    def display_image(self): # display depth image to gui
        print(self.depth_image)
    
    def collect_image(self, line):
        depth_line = line.decode("utf-8").split(',')
        remove_white_space = []
        for substring in depth_line:
            remove_white_space.append(substring.strip())
        clean_depth_line = [x for x in remove_white_space if bool(re.search(r'\d', x))]
        if(self.image_line % 2):
            self.depth_image.append(clean_depth_line)
        else:
            self.depth_image.insert(0, clean_depth_line)
        self.image_line = self.image_line + 1
        if self.image_line > 7:
            self.display_image()
            self.depth_image.clear() # clears all lines out of the depth image
            self.image_line = 0
    
    def command_line(self):
        while len(self.serial_list) > 0:
            line = self.serial_list[0]
            if(b'\n' in line):
                if(self.depth_match_pattern.match(line)): # change to match a line which has only depth pixel data
                    self.collect_image(line)
                else:
                    self.depth_image.clear() # clears all lines out of the depth image if output is interrupted
                    self.image_line = 0
                self.cmd_line.insert(tk.END, line)
                if(self.cmd_line.size() > 25):
                    self.cmd_line.delete(0)
            else:
                self.serial_line = line
            self.serial_list.remove(line)

    def update_display(self):
        if(self.ser.is_open):
            self.connectbutton["bg"] = "green"
        else:
            self.connectbutton["bg"] = "red"
        self.serial_ports()
        self.serial_read()
        self.command_line()
        self.after(100, self.update_display)


if __name__ == "__main__":
    app = MainGui()
    app.mainloop()
