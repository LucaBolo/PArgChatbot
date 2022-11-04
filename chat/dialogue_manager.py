from flask import Blueprint

from .argumentation import ArgumentationManager


dialogue_blueprint = Blueprint('dialogue_manager', __name__)

@dialogue_blueprint.route("/start", methods=("GET",))
def start_conversation():
    return """Hello, I will help you decide where you can vaccinate for Covid19. I am going to ask you
    a series of questions to give you the best answer. This information will never leave your device. Is it ok?"""

@dialogue_blueprint.route("/chat", methods=("GET",))
def chat(user_msg: str):

    reply, elicit = ArgumentationManager.choose_reply(user_msg)

    if not elicit:
        return {"data": reply}