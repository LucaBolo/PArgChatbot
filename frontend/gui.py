from tkinter import *
from tkinter import ttk
import queue, os, sys
import argparse

from controller import Controller
from language.svm.svm import DialogueActClassifier
from language.multilingual.teacher_student import SentenceTranslationEmbedding

class MainWindow:

    def __init__(self, visualize=False) -> None:
        self.window = Tk()
        self.window.title("CovBot")
        self.mainframe = ttk.Frame(self.window, width=640, height=480)
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S), columnspan=3, rowspan=4)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1) 
        

        self.chat_area = Text(self.mainframe, borderwidth=5, font="arial")
        self.chat_area.grid(column=1, row=1, padx=10, pady=20, columnspan=2)

        self.input_area = Text(self.mainframe, height=3, font="arial")
        self.input_area.grid(column=1, row=2, padx=10, pady=10, rowspan=2, columnspan=1)

        self.queue = queue.Queue()
        self.graph_window_queue = None
        self.controller = Controller(self, self.queue, self.graph_window_queue)

        for child in self.window.winfo_children(): 
            child.grid_configure(padx=20, pady=5)

        
        self.start_button = ttk.Button(self.mainframe, text='Start!', command=self.controller.start_conversation)
        self.start_button.grid(column=2, row=2, padx=10, pady=5, columnspan=1)
        self.stop_button = ttk.Button(self.mainframe, text='Stop!', command=self.controller.stop_conversation)
        self.stop_button.grid(column=2, row=3, padx=10, pady=5, columnspan=1)
        
        self.input_area["state"] = "disabled"
        self.stop_button["state"] = "disabled"

        self.input_area.bind('<Return>', self.controller.post_user_message)
        self.window.protocol("WM_DELETE_WINDOW", self.controller.on_close)

        

        if visualize:
            self.graph_window = GraphWindow(self.window)
            self.graph_window_queue = queue.Queue()
            self.controller.set_graph_window_queue(self.graph_window_queue)
            self.process_graph_window_queue()
        
        

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
                
                self.window.after(500, self.process_queue)
        except queue.Empty:
            self.window.after(500, self.process_queue)

    def process_graph_window_queue(self):
        '''Checks for updates in the 
        graph statistics window'''
        try:
            msg = self.graph_window_queue.get_nowait()
            self.graph_window.history.set(f"Arguments: {msg['history_args']}\n Replies: {msg['history_replies']}\n")
                
            self.window.after(1000, self.process_graph_window_queue)
        except queue.Empty:
            self.window.after(1000, self.process_graph_window_queue)

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

    def start_state(self):
        '''Updates widgets' state after
        start button click'''
        self.start_button["state"] = "disabled"
        self.input_area["state"] = "normal"
        self.stop_button["state"] = "normal"

    def stop_state(self):
        '''Updates widgets' state after
        stop button click'''
        self.chat_area["state"] = "disabled"
        self.input_area["state"] = "disabled"
        self.stop_button["state"] = "disabled"
        self.start_button["state"] = "normal"


class GraphWindow(Toplevel):

    def __init__(self, parent, history=None):
        super().__init__(parent)

        self.geometry('300x100')
        self.title('Graph Statistics')

        self.history = StringVar()
        self.label = ttk.Label(self, text=self.history.get())
        self.label.pack()
        
        
        self.label['textvariable'] = self.history
        self.history.set("Arguments: \n" + "Replies: \n")
        

        #resultsContents = StringVar()
        #label['textvariable'] = resultsContents
        #resultsContents.set('New value to display')
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog = 'PArgChatbot', description = 'A privacy-preserving dialogue system based on argumentation and sentence similarity, dealing with Covid19')
    parser.add_argument('--train', type=str, required=False, choices=['sbert', 'svm'])
    parser.add_argument('--visualize', type=bool, required=False)
    args = parser.parse_args()

    if args.train == 'svm':
        

        dir_path = os.path.dirname(os.path.join(os.getcwd(), __file__))
        
        classifier = DialogueActClassifier(os.path.join(dir_path, "language/svm/diag_act_dataset.csv"), os.path.join(dir_path, "language/svm/svc.joblib"))

        train_texts, test_texts, train_labels, test_labels = classifier.prepare_data()

        model = classifier.train(train_texts, train_labels)
    elif  args.train == 'sbert':

        

        sentence_translation_embedding = SentenceTranslationEmbedding()
        sentences_file, links_file = sentence_translation_embedding.download_tatoeba_dataset()
        sts_file = sentence_translation_embedding.download_sts_dataset()

        train_files, dev_files = sentence_translation_embedding.prepare_tatoeba_dataset(sentences_file, links_file)
        sts_data = sentence_translation_embedding.prepare_sts_dataset(sts_file)

        student, teacher = sentence_translation_embedding.prepare_teacher_student_model()

        train_dataloader, train_loss = sentence_translation_embedding.load_train_dataset(student, teacher, train_files)
        evaluators = sentence_translation_embedding.load_evaluators(student, teacher, dev_files, sts_data)
        sentence_translation_embedding.fit(student, train_dataloader, train_loss, evaluators)
    else:
        
        main_window = MainWindow(visualize=args.visualize)
    
