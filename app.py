# save this as app.py
from flask import Flask
from chat.chatbot import Chatbot


app = Flask(__name__)


@app.route("/")
def hello():   

    chatbot = Chatbot()
    #g.populate_db()
    response = chatbot.chat("I am afflicted with mastocystosis")
    print(response)
    

    chatbot.graph.close()
    
    return "Hello, World!"