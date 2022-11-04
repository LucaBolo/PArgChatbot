from flask import Blueprint

from .argumentation import Argumentation


dialogue_blueprint = Blueprint('dialogue_manager', __name__)

@dialogue_blueprint.route("/")
def start_conversation():
    return """Hello, I will help you decide where you can vaccinate for Covid19. If you suffer from any allergies or
    relevant medical conditions, do share them so that I can find the best response for you."""


def chat(user_msg: str):

    reply, elicit = Argumentation.choose_reply(user_msg)

