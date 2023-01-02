from flask import Blueprint
from flask import request

from chat.argumentation import ArgumentationManager

dialogue_blueprint = Blueprint('dialogue_manager', __name__)
arg_manager = ArgumentationManager()


@dialogue_blueprint.route("/", methods=("GET",))
def start_conversation():
    return {"data": """Hello, I will help you decide where you can vaccinate for Covid19. You may share
    with me any medical condition you suffer or suffered from. This information will never leave your device."""}

@dialogue_blueprint.route("/sentences", methods=("GET",))
def get_kb_sentences():
    return {"data": [sentence for sentence in arg_manager.arg_graph.get_arg_sentences()]}

@dialogue_blueprint.route("/chat", methods=("GET",))
def chat():
    
    usr_intent = request.args["usr_intent"]
    usr_msg =  request.args.getlist("usr_msg")
    if usr_intent == 'yes':
        # user responded affirmatively to question
        # we look for a sentence in the node containing the question with positive class
        usr_msg = arg_manager.arg_graph.get_sentence_corresponding_question(usr_msg[0], 'p')
        
        if usr_msg is None:
            return {"data": "I didn't understand your answer, could you repeat?"}
        usr_msg = [usr_msg]
        
    elif usr_intent == 'no':

        # user responded negatively to question
        # we look for a sentence in the node containing the question with negative class

        usr_msg = arg_manager.arg_graph.get_sentence_corresponding_question(usr_msg[0], 'n')

        if usr_msg is None:
            return {"data": "I didn't understand your answer, could you repeat?"}

        usr_msg = [usr_msg]

    
    reply = arg_manager.choose_reply(usr_msg)
    
    return {"data": reply}


@dialogue_blueprint.route("/close", methods=("GET",))
def clear_history():

    arg_manager.clear()

    return {"data": "QUIT"}