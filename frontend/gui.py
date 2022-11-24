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
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S), columnspan=3, rowspan=3)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1) 

        self.chat_area = Text(self.mainframe, borderwidth=5)
        self.chat_area.grid(column=1, row=1, padx=10, pady=20, columnspan=2)

        self.input_area = Text(self.mainframe, height=3)
        self.input_area.grid(column=1, row=2, padx=10, pady=10, columnspan=1)

        self.queue = queue.Queue()
        self.controller = Controller(self, self.queue)

        for child in self.window.winfo_children(): 
            child.grid_configure(padx=20, pady=5)

        
        self.chat_area["state"] = "disabled"
        self.input_area["state"] = "disabled"        
        
        self.button = ttk.Button(self.mainframe, text='Start!', command=self.controller.start_conversation)
        self.button.grid(column=2, row=2, padx=10, pady=10, columnspan=1)

        
        self.input_area.bind('<Return>', self.controller.post_user_message)
        self.window.protocol("WM_DELETE_WINDOW", self.controller.on_close)

        self.process_queue()
        self.window.mainloop()
    

    def process_queue(self):
        '''Checks for new messages in the queue
        from background threads'''
        try:
            msg = self.queue.get_nowait()
            if msg == "QUIT": # user quits the window
                self.window.destroy()
            else:    
                self.write_chat_area("end", msg)
                if "==END==" in msg: # end of conversation
                    self.chat_area["state"] = "disabled"
                    self.input_area["state"] = "disabled"
                
                self.window.after(500, self.process_queue)
        except queue.Empty:
            self.window.after(500, self.process_queue)

    
    def get_delete_user_input(self, delete=True):
        '''Reads the string user input
        and deletes it, by default'''
        msg = self.input_area.get(1.0, END)
        if delete:
            self.input_area.delete(1.0, END)

        return "\n" + ' '.join(msg.split()) + "\n"

    def write_chat_area(self, index, msg):
        '''Enables chat text area 
        to allow writing function
        then disables it again'''
        self.chat_area["state"] = "normal"
        #self.chat_area.insert("end", msg)
        self.chat_area.insert(index, msg+"\n")
        self.chat_area["state"] = "disabled"


if __name__ == '__main__':
    #current_module_path = os.path.dirname(os.path.realpath(__file__))
    #d_classifier = DialogueActClassifier(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'language\diag_act_dataset.csv'), 
    #    os.path.join(current_module_path, 'language\svc.joblib'))

    # train_texts, test_texts, train_labels, test_labels = d_classifier.prepare_data()
    # model = d_classifier.train(train_texts, train_labels)
    #print(d_classifier.predict(["but of course"]))
    main_window = MainWindow()
    
