
from db.covidVaccine import CovidVaccineGraph
from db.queries import get_sentences_endorsing_response, get_sentences_attacking_response, get_sentences_attacked_by_argument, get_sentences_attacking_argument

class Chatbot:


    def __init__(self) -> None:
        self.history_args = [] # history of arguments communicated by user
        self.history_responses = [] # history of responses given to user
        self.graph = CovidVaccineGraph("neo4j://localhost:7687", "neo4j", "password")

    def explain_why_response(self, response: str):
        '''Retrieves the arguments, among those in the history
        that support the given response.'''

        endorsing_args = get_sentences_endorsing_response(self.graph.driver, response)
        
        # arguments in the status set of arguments already collected
        # for user that also endorse the response
        supporting_status_args = [arg_sentence for arg_sentence in endorsing_args if arg_sentence in self.history_args]

        return supporting_status_args


    def explain_why_not_response(self, response: str):
        '''Retrieves the arguments, among those in the history
        that attack the given response'''  

        attacking_args = get_sentences_attacking_response(self.graph.driver, response)

        # arguments in the status set of arguments already collected
        # for user that also attack the response
        attacking_status_arg = [arg_sentence for arg_sentence in attacking_args if arg_sentence in self.history_args]

        return attacking_status_arg

    def is_conflict_free(self, argument: str):
        '''Checks whether the given argument
        is in conflict with the ones in the history'''

        attacked = get_sentences_attacked_by_argument(self.graph.driver, argument)

        # if there is no common sentence between history and the attacks 
        # to the given argument, then it is conflict free
        return set(attacked) & set(self.history_args)

    
    def is_consistent_reply(self, response: str):
        '''Checks whether the reply is consistent. By definition, it is consistent
        if reply is endorsed by the history of arguments, and if it is acceptable, meaning
        if every attack to the reply is attacked by the history. Also, the history must be 
        conflict-free'''

        # if no argument endorses the response then it is not consistent
        if not len(self.explain_why_response(response)):
            return False

        attacking_args = get_sentences_attacking_response(self.graph.driver, response)

        for attacking_arg in attacking_args:

            # see if it is attacked by something in the history
            counterattacking_args = get_sentences_attacking_argument(self.graph.driver, attacking_arg)
            # if no counterattacking argument is found in the history
            # then it is not acceptable
            if set(counterattacking_args) & set(self.history_args):
                return False

        return True

