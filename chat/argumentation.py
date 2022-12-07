from neo4j.graph import Node
import time

from chat.db.CovidVaccineGraph import CovidVaccineGraph




class ArgumentationManager:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ArgumentationManager, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.arg_graph = CovidVaccineGraph()
        self.clear()

    def clear(self):
        # self.history_args = [] # history of argument nodes communicated by user
        self.history_replies = [] # history of reply nodes given to user
        self.history_args = []
        self.potentially_cons_replies = set()

    def explain_why_reply(self, reply: str):
        '''Retrieves the argument nodes, among those in the history
        that support the given reply.'''

        endorsing_args = self.arg_graph.get_arguments_endorsing_reply(reply)
        
        supporting_status_args = [node for node in endorsing_args if node in self.history_args]
        
        return supporting_status_args


    def explain_why_not_reply(self, reply: str):
        '''Retrieves the argument nodes, among those in the history
        that attack the given reply'''  

        attacking_args = self.arg_graph.get_arguments_attacking_reply(reply)
        
        
        # arguments in the status set of arguments already collected
        # for user that also attack the reply
        attacking_status_arg = [node for node in attacking_args if node in self.history_args_id]

        return attacking_status_arg

    def build_explanation(self, reply: str):

        replies = self.arg_graph.get_reply_nodes_labels()
        discarded_replies = list(filter(lambda r : reply != r, replies))
        #print(self.explain_why_reply(reply))
        supporting_args_sentences = [self.arg_graph.get_arg_sentence(why) for why in self.explain_why_reply(reply)]

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
            
            explanation += f"You can't {self.arg_graph.get_arg_sentence(discarded_reply).lower().replace('.', ' with ')} because \n"
            whynots = self.explain_why_not_reply(discarded_reply)
            #print(whynots)
            for whynot in whynots:
                #print(whynot.get("sentences")[0])
                
                explanation += replace_template(self.arg_graph.get_arg_sentence(whynot)) + "\n"

            explanation += "\n"
        
        return explanation                

    def is_conflict_free(self, argument: str):
        '''Checks whether the given argument
        is in conflict with the ones in the history'''

        attacked = self.arg_graph.get_arguments_attacked_by_argument(argument)

        # if there is no common node between history and the attacks 
        # to the given argument, then it is conflict free
        return not (attacked & self.history_args)

    
    def is_consistent_reply(self, reply: str):
        '''Checks whether the reply is consistent. By definition, it is consistent
        if reply is endorsed by the history of arguments, and acceptable, meaning
        if every attack to the reply is attacked by the history. History must
        be a conflict-free set'''


        attacking_args = self.arg_graph.get_arguments_attacking_reply(reply)

        for attacking_arg in attacking_args:

            # see if it is attacked by something in the history
            counterattacking_args = self.arg_graph.get_arguments_attacking_argument(attacking_arg)

            # if no counterattacking argument is found in the history
            # then it is not consistent
            if not (counterattacking_args & self.history_args):
                return False

        return True

    def add_argument(self, arg: str):
        '''Adds node to history if it is not already present'''
        
        if arg not in self.history_args:

            self.history_args.append(arg)

    def add_potentially_cons_replies(self, replies: 'list[str]'):
        '''Adds replies to the potentially_cons replies if 
           1) they are not already present, avoiding duplicates
           2) they are not attacked by arguments in the history'''
        

        for reply in replies:
            if len(self.explain_why_not_reply(reply)) == 0 and reply not in self.potentially_cons_replies:
                self.potentially_cons_replies.add(reply) 

    def choose_reply(self, user_msg: 'list[str]'):
        '''Takes the user message (or rather, the sentences in the KB 
        most similar to the user message), and returns a consistent reply or,
        if absent, information the system needs to turn a potentially consistent
        reply into a consistent one.'''
        # if user message is not an explanation request
        # add it to the arguments in the chat
        
        startime = time.time()
        for sentence in user_msg:
            
            arg_node = self.arg_graph.get_node_containing_sentence(sentence)
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
            replies = self.arg_graph.get_replies_endorsed_by_argument(node)
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
                return self.arg_graph.get_arg_sentence(potentially_cons_reply) + expl + "\n==END==\n"

        for potentially_cons_reply in self.potentially_cons_replies[:]:
            # potentially consistent
            attack_args = self.arg_graph.get_arguments_attacking_reply(potentially_cons_reply)

            # elicit data from user about possible counterattacks
            # this method is called for each message
            # so we need to loop over every attack 
            # first check whether counterattacks are already in history
            # then we ask questions to user only for those that aren't in history
            for attack_arg in attack_args:

                counterattack_args = self.arg_graph.get_arguments_attacking_argument(attack_arg)

                if not any([counterattack_arg in self.history_args for counterattack_arg in counterattack_args]):
                    # if there isn't even a single counter attack 
                    # in the history we must elicit info
                    return self.arg_graph.get_arg_question(counterattack_args)
            

        return "No consistent answer has been found"
