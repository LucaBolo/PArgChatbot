from tkinter import *
from tkinter import ttk
import queue

import requests

from controller import Controller

class MainWindow:

    def __init__(self) -> None:
        self.window = Tk()
        self.window.title("CovBot")
        self.mainframe = ttk.Frame(self.window, width=640, height=480)
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1) 

        self.chat_area = Text(self.mainframe, padx=10, pady=10, borderwidth=5)
        self.chat_area.grid(column=2, row=2, padx=10, pady=20)

        self.input_area = Text(self.mainframe, height=3)
        self.input_area.grid(column=2, row=3)

        for child in self.window.winfo_children(): 
            child.grid_configure(padx=20, pady=5)

        first_msg = requests.get("http://127.0.0.1:5000")

        if first_msg.status_code == 200:
            
            self.chat_area.insert("1.0", ' '.join(first_msg.json()["data"].split()) + "\n\n") # splitting and joining to eliminate tabs and line breaks

        
        self.chat_area["state"] = "disabled"

        
        

        self.queue = queue.Queue()
        self.controller = Controller(self, self.queue)
        self.input_area.bind('<Return>', self.controller.post_user_message)

        self.process_queue()
        self.window.mainloop()
    
    def process_queue(self):
        try:
            msg = self.queue.get_nowait()
            self.write_chat_area("end", msg["data"])
            # Show result of the task if needed
            
        except queue.Empty:
            self.window.after(500, self.process_queue)

    
    def get_delete_user_input(self, delete=True):
        '''Reads the string user input
        and deletes it, by default'''
        msg = self.input_area.get(1.0, END)
        if delete:
            self.input_area.delete(1.0, END)

        return msg

    def write_chat_area(self, index, msg):
        '''Enables chat text area 
        to allow writing function
        then disables it again'''
        self.chat_area["state"] = "normal"
        #self.chat_area.insert("end", msg)
        self.chat_area.insert(index, msg+"\n\n")
        self.chat_area["state"] = "disabled"

    

if __name__ == '__main__':
    main_window = MainWindow()
    
