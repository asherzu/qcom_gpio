
import tkinter as tk
from tkinter import ttk
import re

class SimpleRc(tk.Frame):
    def __init__(self,parent,res=None,resFile=None):
        tk.Frame.__init__(self,parent)
        if res is not None:
            self._parse_rc(res)
        elif resFile is not None:
            self._load_rc(resFile)
    def _parse_rc(self,rc):
        
        pattern = re.compile("(_\w+)\\{0}([^\\{0}]*)\\{0}([^\\{0}]*)\\{0}".format("|"))
        self._widgets={}
        row=1
        lineNum = 0
        for eachLine in re.split("[\r\n]+",rc):
            eachLine = eachLine.strip()
            lineNum = lineNum + 1
            if eachLine == "":
                continue
            if eachLine.startswith("#"):
                continue
            widgetAll = pattern.findall(eachLine)
            if widgetAll == None:
                continue
            column= 0
            for widget in widgetAll:
                type =widget[0]
                value = widget[1]
                name = widget[2]
                wdt = None
                print(name,value)
                if type == "_L":
                    wdt = ttk.Label(self,text=value)
                    wdt.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                elif type == "_E":
                    wdt = ttk.Entry(self)
                    wdt.grid(row=row, column = column, sticky="nsew", padx =1 ,pady =1)
                    if value != "":
                        wdt.insert(tk.END,value)
                elif type == "_B":
                    wdt = ttk.Button(self,text=value)
                    wdt.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                column = column + 1
                if name != "":
                    if name in self._widgets:
                        raise Exception("Found duplicate name {} in {}".format(name,lineNum))
                    self._widgets[name] = wdt
            row = row +1
    def _load_rc(self,file):
        with open(file) as f:
            data = f.read()
            self._parse_rc(data)


if __name__ == "__main__":
    root = tk.Tk()
    rc = SimpleRc(root,resFile="rc.txt")
    rc.pack()
    root.mainloop()
    