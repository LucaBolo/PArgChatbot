import requests
import threading

from language import get_most_similar_sentence

class Controller:

    def __init__(self, gui, queue) -> None:
        self.gui = gui
        self.queue = queue

    
    def post_user_message(self, e):

        msg = self.gui.get_delete_user_input()
        
        self.gui.write_chat_area("end", msg)

        t = threading.Thread(target=self.get_bot_reply, args=(msg,))
        t.start()


    def get_bot_reply(self, msg: str):
        
        res = requests.get("http://127.0.0.1:5000/sentences")

        kb = res.json()["data"]
        sentence = get_most_similar_sentence(msg, kb)

        res = requests.get("http://127.0.0.1:5000/chat", params={"usr_msg": sentence})

        self.queue.put(res.json())