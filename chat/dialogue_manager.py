from flask import Blueprint

from .argumentation import ArgumentationManager


dialogue_blueprint = Blueprint('dialogue_manager', __name__)

@dialogue_blueprint.route("/", methods=("GET",))
def start_conversation():
    return {"data": """Hello, I will help you decide where you can vaccinate for Covid19. You may share
    with me any medical condition you suffer or suffered from. This information will never leave your device."""}



@dialogue_blueprint.route("/chat", methods=("GET",))
def chat(user_msg: str):

    reply, elicit = ArgumentationManager.choose_reply(user_msg)

    if not elicit:
        return {"data": reply}