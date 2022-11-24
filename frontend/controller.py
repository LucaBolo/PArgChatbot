import os, json, threading, requests

from language.language import get_most_similar_sentence
from language.svm import DialogueActClassifier


class Controller:

    def __init__(self, gui, queue) -> None:
        self.gui = gui
        self.queue = queue
        self.dialog_classifier = DialogueActClassifier('./language/diag_act_dataset.csv', './language/svc.joblib')
        self.last_bot_response = None

    
    def post_user_message(self, e):
        '''Copies user input in chat area
        then requests the server for a reply'''
        msg = self.gui.get_delete_user_input()
        self.gui.write_chat_area("end", msg)

        t = threading.Thread(target=self.get_bot_reply, args=(msg,))
        t.start()


    def get_bot_reply(self, msg: str):
        
        if os.path.exists('./language/kb_embs.json'):
            with open('./language/kb_embs.json') as f:
                kb = list(json.load(f).keys())
        else:
            res = requests.get("http://127.0.0.1:5000/sentences")
            kb = res.json()["data"]
        sentence, distance = get_most_similar_sentence(msg, kb)
        
        intent = 'other'
        if distance > 0.4: # threshold for now arbitrary
            # user message isn't close enough to sentences in kb
            # so the sentence we send to server is the last response
            # and we classify the intent of the user
            intent = self.dialog_classifier.predict(msg)
            sentence = self.last_bot_response 
            
        res = requests.get("http://127.0.0.1:5000/chat", params={"usr_msg": sentence, "usr_intent": intent})
        self.last_bot_response = res.json()["data"]
        self.queue.put(self.last_bot_response)

    def on_close(self):

        def clear_history():
            res = requests.get("http://127.0.0.1:5000/close")

            self.queue.put(res.json()["data"])


        t = threading.Thread(target=clear_history)
        t.start()

    def start_conversation(self):


        def greeting():
            requests.get("http://127.0.0.1:5000/close")
            first_msg = requests.get("http://127.0.0.1:5000")

            greeting = ' '.join(first_msg.json()["data"].split()) + "\n"
            #self.write_chat_area("end", greeting) # splitting and joining to eliminate tabs and line breaks

            self.queue.put(greeting)

        self.gui.button["state"] = "disabled"
        self.gui.input_area["state"] = "normal"
        t = threading.Thread(target=greeting)
        t.start()
        
        
        

