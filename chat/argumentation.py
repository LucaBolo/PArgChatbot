from neo4j.graph import Node

from .db.covidVaccine import CovidVaccineGraph
from .db.queries import (get_arguments_endorsing_reply, 
                        get_arguments_attacking_reply, 
                        get_arguments_attacked_by_argument, 
                        get_arguments_attacking_argument,
                        get_node_containing_sentence,
                        get_replies_endorsed_by_argument)

class ArgumentationManager:


    def __init__(self) -> None:
        self.history_args = [] # history of argument nodes communicated by user
        self.history_replies = [] # history of reply nodes given to user
        self.history_args_id = set()
        self.candidate_replies = []
        self.graph = CovidVaccineGraph("neo4j://localhost:7687", "neo4j", "password")


    def explain_why_reply(self, reply: Node):
        '''Retrieves the argument nodes, among those in the history
        that support the given reply.'''

        endorsing_args = get_arguments_endorsing_reply(self.graph.driver, reply)

        supporting_status_args = [node for node in endorsing_args if node.id in self.history_args_id]

        return supporting_status_args


    def explain_why_not_reply(self, reply: Node):
        '''Retrieves the argument nodes, among those in the history
        that attack the given reply'''  

        attacking_args = get_arguments_attacking_reply(self.graph.driver, reply)

        # arguments in the status set of arguments already collected
        # for user that also attack the reply``
        attacking_status_arg = [node for node in attacking_args if node.id in self.history_args_id]

        return attacking_status_arg

    def is_conflict_free(self, argument: Node):
        '''Checks whether the given argument
        is in conflict with the ones in the history'''

        attacked = get_arguments_attacked_by_argument(self.graph.driver, argument)

        attacked_ids = {node.get("id") for node in attacked}
        # if there is no common node between history and the attacks 
        # to the given argument, then it is conflict free
        return not (attacked_ids & self.history_args_id)

    
    def is_consistent_reply(self, reply: Node):
        '''Checks whether the reply is consistent. By definition, it is consistent
        if reply is endorsed by the history of arguments, and acceptable, meaning
        if every attack to the reply is attacked by the history. Precondition, history must
        be a conflict-free set'''


        attacking_args = get_arguments_attacking_reply(self.graph.driver, reply)

        for attacking_arg in attacking_args:

            # see if it is attacked by something in the history
            counterattacking_args = get_arguments_attacking_argument(self.graph.driver, attacking_arg)

            counterattacking_args_id = {node.get(id) for node in counterattacking_args}
            # if no counterattacking argument is found in the history
            # then it is not acceptable
            if not (counterattacking_args_id & self.history_args_id):
                return False

        return True


    def add_candidate_replies(self, replies: 'list[Node]'):
        '''Adds replies to the candidate replies if 
           1) they are not already present, avoiding duplicates
           2) they are not attacked by arguments in the history'''
        candidate_reply_ids = [reply.get('id') for reply in self.candidate_replies]
        
        for reply in replies:
            if len(self.explain_why_not_reply(reply)) == 0 and reply.get("id") not in candidate_reply_ids:
                self.candidate_replies.append(reply) 

    def choose_reply(self, user_msg: str):
        '''Takes the user message (or rather, the sentence in the KB 
        most similar to the user message), and returns a consistent reply or,
        if absent, information the system needs to turn a potentially consistent
        reply into a consistent one. It also points to the caller whether the response
        is an elicitation or not'''
        # if user message is not an explanation request
        # add it to the arguments in the chat
        elicit = False
        arg_node = get_node_containing_sentence(self.graph.driver, user_msg)
        if self.is_conflict_free(arg_node):
            self.history_args.append(arg_node)
            self.history_args_id.add(arg_node.get("id"))
        else:
            return "This user message contradicts previous statements", elicit


        # retrieve the replies endorsed by the user message. If no messages are returned
        replies = get_replies_endorsed_by_argument(self.graph.driver, arg_node)

        if len(replies) == 0 and len(self.candidate_replies) == 0:
            return 'reply not found', elicit

        self.add_candidate_replies(replies)    

        for candidate_reply in self.candidate_replies[:]:
            if self.is_consistent_reply(candidate_reply):
                # append it to history of replies and remove it from candidates
                
                self.history_replies.append(candidate_reply)
                self.candidate_replies.remove(candidate_reply)
                return candidate_reply.get("sentence")[0], elicit

            else:
                # potentially consistent
                attack_args = get_arguments_attacking_reply(self.graph.driver, candidate_reply)

                # elicit data from user about possible counterattacks
                # this method is called for each message
                # so we need to loop over every attack 
                # first check whether counterattacks are already in history
                # then we ask questions to user only for those that aren't in history
                for attack_arg in attack_args:

                    counterattack_args = get_arguments_attacking_argument(self.graph.driver, attack_arg)
                    if not any([counterattack_arg.get("id") in self.history_args_id for counterattack_arg in counterattack_args]):
                        # if there isn't even a single counter attack 
                        # in the history we must elicit info
                        elicit = True
                        return counterattack_args[0].get("sentences")[0], elicit
                # if we reach here, must mean the reply has been made consistent
                return candidate_reply.get("sentence")[0]
                        
