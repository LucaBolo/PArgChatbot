from neo4j.graph import Node
import time

from chat.db.covidVaccine import CovidVaccineGraph
from chat.db.queries import (get_arguments_endorsing_reply, 
                        get_arguments_attacking_reply, 
                        get_arguments_attacked_by_argument, 
                        get_arguments_attacking_argument,
                        get_node_containing_sentence,
                        get_replies_endorsed_by_argument,
                        get_replies)



class ArgumentationManager:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ArgumentationManager, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.graph = CovidVaccineGraph("neo4j://localhost:7687", "neo4j", "password")
        self.clear()

    def clear(self):
        self.history_args = [] # history of argument nodes communicated by user
        self.history_replies = [] # history of reply nodes given to user
        self.history_args_id = set()
        self.potentially_cons_replies = []

    def explain_why_reply(self, reply: Node):
        '''Retrieves the argument nodes, among those in the history
        that support the given reply.'''

        endorsing_args = get_arguments_endorsing_reply(self.graph.driver, reply)
        
        supporting_status_args = [node for node in endorsing_args if node.get("id") in self.history_args_id]
        
        return supporting_status_args


    def explain_why_not_reply(self, reply: Node):
        '''Retrieves the argument nodes, among those in the history
        that attack the given reply'''  

        attacking_args = get_arguments_attacking_reply(self.graph.driver, reply)
        
        
        # arguments in the status set of arguments already collected
        # for user that also attack the reply
        attacking_status_arg = [node for node in attacking_args if node.get("id") in self.history_args_id]

        return attacking_status_arg

    def build_explanation(self, reply: Node):

        replies = get_replies(self.graph.driver)
        discarded_replies = list(filter(lambda r : reply.get("id") != r.get("id"), replies))
        #print(self.explain_why_reply(reply))
        supporting_args_sentences = [why.get("sentences")[0] for why in self.explain_why_reply(reply)]

        #print(supporting_args_sentences)
        template_args = {
            "I": "You",
            "I am": "You are",
            "I'm": "You are",
            "me": "you"
        }

        def replace_template(sentence):
            for k, v in template_args.items():
                sentence = sentence.replace(k,v)
            return sentence

        explanation = ".\nThis answer is supported by what you said: \n" + ', '.join([replace_template(supporting_arg_sentence) for supporting_arg_sentence in supporting_args_sentences])
            
        explanation += "\n\n"

        for discarded_reply in discarded_replies:
            
            explanation += f"You can't {discarded_reply.get('sentence')[0].lower().replace('.', ' with ')} because \n"
            whynots = self.explain_why_not_reply(discarded_reply)
            #print(whynots)
            for whynot in whynots:
                #print(whynot.get("sentences")[0])
                
                explanation += replace_template(whynot.get("sentences")[0]) + "\n"

            explanation += "\n"
        
        return explanation                

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

    def add_argument(self, arg_node):
        '''Adds node to history if it is not already present'''
        
        if arg_node.get("id") not in self.history_args_id:

            self.history_args.append(arg_node)
            self.history_args_id.add(arg_node.get("id"))

    def add_potentially_cons_replies(self, replies: 'list[Node]'):
        '''Adds replies to the potentially_cons replies if 
           1) they are not already present, avoiding duplicates
           2) they are not attacked by arguments in the history'''
        

        potentially_cons_reply_ids = [reply.get('id') for reply in self.potentially_cons_replies]

        for reply in replies:
            if len(self.explain_why_not_reply(reply)) == 0 and reply.get("id") not in potentially_cons_reply_ids:
                self.potentially_cons_replies.append(reply) 

    def choose_reply(self, user_msg: 'list[str]'):
        '''Takes the user message (or rather, the sentences in the KB 
        most similar to the user message), and returns a consistent reply or,
        if absent, information the system needs to turn a potentially consistent
        reply into a consistent one.'''
        # if user message is not an explanation request
        # add it to the arguments in the chat
        
        startime = time.time()
        for sentence in user_msg:
            
            arg_node = get_node_containing_sentence(self.graph.driver, sentence)
            if self.is_conflict_free(arg_node):
                self.add_argument(arg_node)

            else:
                return "Your message contradicts previous statements"
        print(time.time() - startime)
        # filter past potentially consistent replies that are no longer compatible with newly added arguments
        # explain why not retrieves argument in the history attacking the given reply
        self.potentially_cons_replies = list(filter(lambda potentially_cons_reply : len(self.explain_why_not_reply(potentially_cons_reply)) == 0, self.potentially_cons_replies))

        # retrieve the replies endorsed by the nodes activated by user's message.
        # add them to potentially consistent replies if not duplicates
        for node in self.history_args:
            replies = get_replies_endorsed_by_argument(self.graph.driver, node)
            self.add_potentially_cons_replies(replies)

        
        if len(replies) == 0 and len(self.potentially_cons_replies) == 0:
            return 'No consistent answer has been found'    
            
        # if there is even a single consistent reply we return it to the user
        for potentially_cons_reply in self.potentially_cons_replies[:]:
            if self.is_consistent_reply(potentially_cons_reply):
                # append it to history of replies and remove it from potentially_conss
                
                self.history_replies.append(potentially_cons_reply)
                self.potentially_cons_replies.remove(potentially_cons_reply)

                expl = self.build_explanation(potentially_cons_reply)
                return potentially_cons_reply.get("sentence")[0] + expl + "\n==END==\n"

        for potentially_cons_reply in self.potentially_cons_replies[:]:
            # potentially consistent
            attack_args = get_arguments_attacking_reply(self.graph.driver, potentially_cons_reply)

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
                    return counterattack_args[0].get("question") 
            

        return "No consistent answer has been found"
