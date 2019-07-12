import time
import os
import re
import subprocess

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element,SubElement, Comment,tostring
from xml.dom import minidom
from simple_resource import SimpleRc

import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
from matplotlib.figure import Figure


LARGE_FONT = ('Verdana', 12)
NORMAL_FONT = ('Verdana', 10)
SMALL_FONT = ('Verdana', 8)

def set_bits(value, offset,mask):
    return value|(mask<<offset)
def clear_bits(value,offset,mask):
    return value & ~(mask<<offset)
class AssaistantApp(tk.Tk):
    def __init__(self, *args, **kargs):
        tk.Tk.__init__(self,*args,**kargs)
        # tk.Tk.iconbitmap(self, default="nand.icon")
        tk.Tk.wm_title(self, "Assistant")
        
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        
        self.create_frames(container)
        
        self.create_menubar(container)
        self.frames[HomeFrame].append_buttons(self.frames,self)
    def create_frames(self, container):
        self.frames = {}
        for frameClass in (HomeFrame,DisableVerity,GPIOFrame):
            frame = frameClass(container, self)
            self.frames[frameClass] = frame
            frame.grid(row= 0, column= 0, sticky = "nsew")
        self.show_frame(HomeFrame)
    def create_menubar(self,container):
        menubar = tk.Menu(container)
        
        fileMenu = tk.Menu(menubar,tearoff=0)
        for F in self.frames:
            name = self.frames[F].get_name()
            fileMenu.add_command(label=name,command=lambda F= F: self.show_frame(F))
        # fileMenu.add_command(label="Save picture",command=lambda:self.save_picture())
        menubar.add_cascade(label= "Utils",menu=fileMenu)
        
        
        tk.Tk.config(self,menu=menubar)
    def show_frame(self,frame):
        if frame in self.frames:
            self.frames[frame].tkraise()
            print("tkraise {}".format(self.frames[frame].get_name()))
        else:
            print("Error in show_frame");
class HomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = ttk.Label(self, text="Home Page", font= LARGE_FONT)
        label.pack(padx=10,pady=10)
        
    def get_name(self):
        return "Home"
    def append_buttons(self,frames,controller):
        for F in frames:
            name = frames[F].get_name()
            button = ttk.Button(self, text=name,command=lambda F=F: controller.show_frame(F))
            button.pack()
def shell(cmd):
    process = subprocess.run(cmd,stdout=subprocess.PIPE)
    return process.stdout.decode()
def adb_shell(serial,command):
    if serial == None:
        cmds = ["adb", "shell",command]
    else:
        cmds=["adb","-s",serial, "shell",command]
    return shell(cmds)
def adb(serial,command):
    if serial == None:
        cmds = ["adb", command]
    else:
        cmds=["adb","-s",serial,command]
    return shell(cmds)
def adb_devices():
    cmd=["adb","devices"]
    result= shell(cmd)
    patern = re.compile("(\w+)\s+device[\n\r]")
    
    return patern.findall(result)
    
def alert(msg):
    popup = tk.Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font=NORMAL_FONT)
    label.pack(side="top", fill="x", pady = 10)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()
def show_text(msg):
    popup = tk.Tk()
    popup.wm_title("!")
    
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    label = ttk.Label(popup, text=msg, font=NORMAL_FONT)
    label.pack(side="top", fill="x", pady = 10)
    popup.mainloop()
class DisableVerity(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = ttk.Label(self, text="Disable verity", font= LARGE_FONT)
        label.pack(padx=10,pady=10)
        button = ttk.Button(self, text="home",command=lambda: controller.show_frame(HomeFrame))
        button.pack(padx=10,pady=10)
        buttonDisable=ttk.Button(self, text="Start", command=lambda: self.disable_verity())
        
        buttonDisable.pack()
        label =  ttk.Label(self, text="Status")
        label.pack(padx=10,pady=10)
        self.status= label
    def get_name(self):
        return "Disable verity"
    def update_status(self,text,background="white"):
        self.status.config(text=text,background=background)
        self.status.update_idletasks()
    def disable_verity(self):
        patern = re.compile("(\w+)\s+device")
        serials = adb_devices()
        if serials == []:
            self.update_status("Not found devices","red")
            return
        for serial in serials:
            self.update_status("root")
            adb(serial,"root")
            time.sleep(1)
            count= 0
            while serial not in adb_devices() and count < 5:
                time.sleep(1)
                count = count +1
            result = adb(serial,"disable-verity")
            if result.startswith("Verity already disabled on /system"):
                self.update_status("success","green")
                continue
            if result.startswith("Verity disabled on /system"):
                self.update_status("success and reboot","green")
                adb(serial,"reboot")
                continue
            print("Unhandle result"+result)
class GPIOFrame(SimpleRc):
    def get_name(self):
        return "GPIO"
    def __init__(self,parent,controller):
        SimpleRc.__init__(self,parent,resFile="gpio_rc.txt")
        self._widgets['read'].config(command=lambda:self.read())
        self._widgets['write'].config(command=lambda:self.write())
        self._widgets['help'].config(command=lambda:self.help())
        
    def help(self):
        show_text(
        """MSM8095
0x01000000 0x1000*n TLMM_GPIO_CFGn, n=[0..112]








""")
    def read_register(self,serials,program,addr):
        result=adb_shell(serials[0],"{} 0x{:x}".format(program,addr))
        print(result)
        patern = re.compile("(\w+):\s+(\w+)")
        map=patern.findall(result)
        print(map)
        if map == []:
            alert("Decode error")
            return
        value= int(map[0][1],16)
        print("0x{:x}: 0x{:x}".format(addr,value))
        return value
    def write_register(self,serials,program,addr,value):
        return adb_shell(serials[0],"{} 0x{:x} 0x{:x}".format(program,addr,value))
    def read(self):
        prog = self._widgets['program'].get()
        
        base = int(self._widgets['baseAddr'].get(),16)
        offset=int(self._widgets['offset'].get(),16)
        num =  int(self._widgets['gpioNum'].get(),10)
        print("Read base 0x{:x} offset 0x{:x} gpio number {}".format(base,offset,num))
        addr= base + offset*num
        print("Read Address:0x{:x}".format(addr))
        serials = adb_devices()
        if serials == []:
            alert("Not device")
            return
        value = self.read_register(serials,prog,addr)
        FUNC_SEL=0xF & (value >> 2)#5:2
        self._widgets['fun'].delete(0, tk.END)
        self._widgets['fun'].insert(tk.END, str(FUNC_SEL))
        
        GPIO_PULL= 0x3 & (value)#1:0
        pull_map=["NO_PULL", "PULL_DOWN","KEEPER","PULL_UP"]
        print("GPIO_PULL",GPIO_PULL)
        self._widgets['pull'].delete(0,tk.END)
        self._widgets['pull'].insert(tk.END,pull_map[GPIO_PULL])
        
        DRV_STRENGTH = 0x7 & (value>>6)#8:6
        drv_map=["2ma","4ma","6ma","8ma","10ma","12ma","14ma","16ma"]
        self._widgets['drv'].delete(0,tk.END)
        self._widgets['drv'].insert(tk.END,drv_map[DRV_STRENGTH])
        
        GPIO_OUT = 1&(value >>9)
        
        self._widgets['dir'].delete(0,tk.END)
        print("GPIO_OUT",GPIO_OUT)
        if GPIO_OUT == 1:
            self._widgets['dir'].insert(tk.END,"out")
        else:
            self._widgets['dir'].insert(tk.END,"in")
        
        value = self.read_register(serials,prog,addr+4)
        
        self._widgets['GPIO_OUT'].delete(0,tk.END)
        self._widgets['GPIO_IN'].delete(0,tk.END)
        self._widgets['GPIO_OUT'].insert(tk.END,str(value>>1 & 1))
        self._widgets['GPIO_IN'].insert(tk.END,str(value& 1))
        self.refresh()
    def refresh(self):
        for w in self._widgets.values():
            w.update_idletasks()
    def write(self):
        prog = self._widgets['program'].get()
        
        base = int(self._widgets['baseAddr'].get(),16)
        offset=int(self._widgets['offset'].get(),16)
        num =  int(self._widgets['gpioNum'].get(),10)
        print("Read base 0x{:x} offset 0x{:x} gpio number {}".format(base,offset,num))
        addr= base + offset*num
        print("Read Address:0x{:x}".format(addr))
        serials = adb_devices()
        if serials == []:
            alert("Not device")
            return
        
        TLMM_GPIO_CFGn= self.read_register(serials,prog,addr)
        print("0x{:x}: 0x{:x}".format(addr,TLMM_GPIO_CFGn))
        
        TLMM_GPIO_IN_OUT= self.read_register(serials,prog,addr+4)
        print("before TLMM_GPIO_CFGn {:x} {:x}".format(TLMM_GPIO_CFGn,TLMM_GPIO_IN_OUT))
        GPIO_OUT = int(self._widgets['GPIO_OUT'].get())
        
        if "out" == self._widgets['dir'].get():
            TLMM_GPIO_CFGn = set_bits(TLMM_GPIO_CFGn,9,1)
            TLMM_GPIO_IN_OUT = clear_bits(TLMM_GPIO_IN_OUT,1,0x1)
            TLMM_GPIO_IN_OUT = set_bits(TLMM_GPIO_IN_OUT,1,GPIO_OUT)
        else:
            TLMM_GPIO_CFGn = clear_bits(TLMM_GPIO_CFGn,9,1)
        
        #DRV_STRENGTH = 0x7 & (value>>6)#8:6
        drv_map=["2ma","4ma","6ma","8ma","10ma","12ma","14ma","16ma"]
        drv=self._widgets['drv'].get()
        try:
            off = drv_map.index(drv)
            TLMM_GPIO_CFGn = clear_bits(TLMM_GPIO_CFGn,6,0x7)
            TLMM_GPIO_CFGn = set_bits(TLMM_GPIO_CFGn,6,off)
        except Exception as e:
            alert("Wrong input Drive")
            return
        #FUNC_SEL=0xF & (value >> 2)#5:2
        FUNC_SEL = int(self._widgets['fun'].get())
        TLMM_GPIO_CFGn = clear_bits(TLMM_GPIO_CFGn,2,0xF)
        TLMM_GPIO_CFGn = set_bits(TLMM_GPIO_CFGn,2,FUNC_SEL)
        
        #GPIO_PULL= 0x3 & (value)#1:0
        pull_map=["NO_PULL", "PULL_DOWN","KEEPER","PULL_UP"]
        pull = self._widgets['pull'].get()
        try:
            off = pull_map.index(pull)
            TLMM_GPIO_CFGn = clear_bits(TLMM_GPIO_CFGn,0,0x3)
            TLMM_GPIO_CFGn = set_bits(TLMM_GPIO_CFGn,0,off)
        except Exception as e:
            alert("Wrong input pull")
            return
        print("after TLMM_GPIO_CFGn {:x} {:x}".format(TLMM_GPIO_CFGn,TLMM_GPIO_IN_OUT))
        result=self.write_register(serials,prog,addr,TLMM_GPIO_CFGn)
        print(result)
        result=self.write_register(serials,prog,addr+4,TLMM_GPIO_IN_OUT)
        print(result)
app = AssaistantApp()
app.geometry("1024x768")
app.mainloop()
