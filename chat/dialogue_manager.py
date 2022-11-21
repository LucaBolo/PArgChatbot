from flask import Blueprint
from flask import request

from .argumentation import ArgumentationManager
from .db.queries import get_sentences, get_argument_from_question

dialogue_blueprint = Blueprint('dialogue_manager', __name__)
arg_manager = ArgumentationManager()


@dialogue_blueprint.route("/", methods=("GET",))
def start_conversation():
    return {"data": """Hello, I will help you decide where you can vaccinate for Covid19. You may share
    with me any medical condition you suffer or suffered from. This information will never leave your device."""}

@dialogue_blueprint.route("/sentences", methods=("GET",))
def get_kb_sentences():
    return {"data": [sentence for sentences in get_sentences(arg_manager.graph.driver) for sentence in sentences]}

@dialogue_blueprint.route("/chat", methods=("GET",))
def chat():
    
    usr_intent = request.args["usr_intent"]
    usr_msg =  request.args["usr_msg"]
    if usr_intent == 'yes':
        # user responded affirmatively to question
        # we look for a sentence in the node containing the question with positive class
        usr_msg = get_argument_from_question(arg_manager.graph.driver, usr_msg, 'p')
        if len(usr_msg):
            usr_msg = usr_msg[0]
        else:
            return {"data": "I didn't understand your answer, could you repeat?"}
    elif usr_intent == 'no':

        # user responded negatively to question
        # we look for a sentence in the node containing the question with negative class
        usr_msg = get_argument_from_question(arg_manager.graph.driver, usr_msg, 'n')
        if len(usr_msg):
            usr_msg = usr_msg[0]
        else:
            return {"data": "I didn't understand your answer, could you repeat?"}
    elif usr_intent == 'why':
        # send explanation to user
        pass
    
    reply = arg_manager.choose_reply(usr_msg)
    
    return {"data": reply}


@dialogue_blueprint.route("/close", methods=("GET",))
def clear_history():

    arg_manager.clear()

    return {"data": "QUIT"}