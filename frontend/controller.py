import os, json, threading, requests

from language.language import get_most_similar_sentence
from language.svm.svm import DialogueActClassifier


class Controller:

    def __init__(self, gui, queue, graph_window_queue=None) -> None:
        self.gui = gui
        self.queue = queue
        self.graph_window_queue = graph_window_queue

        self.last_bot_response = None

        current_module_path = os.path.dirname(os.path.realpath(__file__))
        self.dialog_classifier = DialogueActClassifier(os.path.join(current_module_path, 'language/svm/diag_act_dataset.csv'), 
            os.path.join(current_module_path,'language/svm/svc.joblib'))
        
    def set_graph_window_queue(self, graph_window_queue):
        self.graph_window_queue = graph_window_queue
    
    def post_user_message(self, e):
        '''Copies user input in chat area
        then requests the server for a reply'''
        msg = self.gui.get_delete_user_input()
        self.gui.write_chat_area("end", msg)

        t = threading.Thread(target=self.post_closest_embeddings, args=(msg,))
        t.start()


    def post_closest_embeddings(self, msg: str):
        
        if os.path.exists('./language/kb_embs.json'):
            with open('./language/kb_embs.json') as f:
                kb = list(json.load(f).keys())
        else:
            res = requests.get("http://127.0.0.1:5000/sentences")
            kb = res.json()["data"]
        sentences = get_most_similar_sentence(msg, kb)

        intent = 'other'
        if len(sentences) == 0: 
            # user message isn't close enough to sentences in kb
            # so the sentence we send to server is the last response
            # and we classify the intent of the user
            intent = self.dialog_classifier.predict(msg)
            if intent == '':
                self.queue.put("I'm not sure I understand the answer, could you repeat?")
            else:
                sentences = [self.last_bot_response] if self.last_bot_response is not None else ''

        if intent != '':
            res = requests.get("http://127.0.0.1:5000/chat", params={"usr_msg": sentences, "usr_intent": intent})
            res = res.json()

            self.last_bot_response = res["data"]
            self.queue.put(self.last_bot_response)
            if self.graph_window_queue is not None:
                self.graph_window_queue.put({"history_args": res["history_args"], "history_replies": res["history_replies"]})

    def on_close(self):

        def clear_history():
            res = requests.get("http://127.0.0.1:5000/close")

            self.queue.put(res.json()["data"])

        self.last_bot_response = None
        t = threading.Thread(target=clear_history)
        t.start()

    def start_conversation(self):


        def greeting():
            requests.get("http://127.0.0.1:5000/close")
            first_msg = requests.get("http://127.0.0.1:5000")

            greeting = ' '.join(first_msg.json()["data"].split()) + "\n"
            #self.write_chat_area("end", greeting) # splitting and joining to eliminate tabs and line breaks

            self.queue.put(greeting)

        self.gui.start_state()        
        t = threading.Thread(target=greeting)
        t.start()
        
    def stop_conversation(self):
        
        def end():
            requests.get("http://127.0.0.1:5000/close")
            self.queue.put("==END==")

        self.gui.stop_state()
        t = threading.Thread(target=end)
        t.start()

        
        

