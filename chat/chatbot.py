
from db.covidVaccine import CovidVaccineGraph
from db.queries import (get_arguments_endorsing_response, 
                        get_arguments_attacking_response, 
                        get_arguments_attacked_by_argument, 
                        get_arguments_attacking_argument,
                        get_node_containing_sentence)

class Chatbot:


    def __init__(self) -> None:
        self.history_args = [] # history of argument nodes communicated by user
        self.history_responses = [] # history of response nodes given to user
        self.history_args_id = set()
        self.graph = CovidVaccineGraph("neo4j://localhost:7687", "neo4j", "password")


    def explain_why_response(self, response: str):
        '''Retrieves the argument nodes, among those in the history
        that support the given response.'''

        endorsing_args = get_arguments_endorsing_response(self.graph.driver, response)

        supporting_status_args = [node for node in endorsing_args if node.id in self.history_args_id]

        return supporting_status_args


    def explain_why_not_response(self, response: str):
        '''Retrieves the argument nodes, among those in the history
        that attack the given response'''  

        attacking_args = get_arguments_attacking_response(self.graph.driver, response)

        # arguments in the status set of arguments already collected
        # for user that also attack the response
        attacking_status_arg = [node for node in attacking_args if node.id in self.history_args_id]

        return attacking_status_arg

    def is_conflict_free(self, argument: str):
        '''Checks whether the given argument
        is in conflict with the ones in the history'''

        attacked = get_arguments_attacked_by_argument(self.graph.driver, argument)

        attacked_ids = {node.get("id") for node in attacked}
        # if there is no common node between history and the attacks 
        # to the given argument, then it is conflict free
        return not (attacked_ids & self.history_args_id)

    
    def is_consistent_reply(self, response: str):
        '''Checks whether the reply is consistent. By definition, it is consistent
        if reply is endorsed by the history of arguments, and acceptable, meaning
        if every attack to the reply is attacked by the history. Returns -1 if the response/reply
        is not endorsed by anything, 1 if it is consistent, 0 if only partially inconsistent'''

        # if no argument endorses the response then it is not consistent
        if not len(self.explain_why_response(response)):
            return -1

        attacking_args = get_arguments_attacking_response(self.graph.driver, response)

        for attacking_arg in attacking_args:

            # see if it is attacked by something in the history
            counterattacking_args = get_arguments_attacking_argument(self.graph.driver, attacking_arg)

            counterattacking_args_id = {node.get(id) for node in counterattacking_args}
            # if no counterattacking argument is found in the history
            # then it is not acceptable
            if not (counterattacking_args_id & self.history_args_id):
                return 0

        return 1

    def chat(self, user_msg: str):
        reply = None
        # if user message is not an explanation request
        # add it to the arguments in the chat
        if self.is_conflict_free(user_msg):
            arg_node = get_node_containing_sentence(self.graph, user_msg)
            self.history_args.append(arg_node)
            self.history_args_id.add(arg_node.id)


        # retrieve the replies endorsed by the user message. If no messages are returned
        # check if there is an endorsed reply that is consistent. If it is return it
        # if it is instead potentially consistent, we must elicit further information from the user