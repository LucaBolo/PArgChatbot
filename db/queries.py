from neo4j import Neo4jDriver


def get_arguments_attacking_response(driver: Neo4jDriver, response: str):
    '''Returns the attacking arguments to this response, flattened'''
    with driver.session() as session:

        attacking_args = session.run("""MATCH (a:arg)-[:attack]->(re:reply) 
                                        WHERE $response IN re.sentence
                                        RETURN a""", response=response)
        # WHERE $response IN a.sentences 
        # WITH COLLECT(DISTINCT a.sentences) as kb
        # [s in kb WHERE s IN  $status] as attacking_args
        return attacking_args.value()


def get_arguments_attacking_argument(driver: Neo4jDriver, argument: str):
    '''Returns the attacking arguments to this argument,
    usually just its negated, flattened'''
    with driver.session() as session:

        attacking_args = session.run("""MATCH (a1:arg)-[:attack]->(a2:arg) 
                                        WHERE $argument IN a2.sentences
                                        RETURN a1""", argument=argument)
        
        return attacking_args.value()


def get_arguments_endorsing_response(driver: Neo4jDriver, response: str):
    '''Returns the arguments that endorse this response, flattened'''
    with driver.session() as session:

        endorsing_args = session.run("""MATCH (a:arg)-[:endorse]->(re:reply) 
                                        WHERE $response IN re.sentence
                                        RETURN a""", response=response)
        
        return endorsing_args.value()

def get_arguments_attacked_by_argument(driver: Neo4jDriver, argument: str):
    '''Returns the argument nodes attacked by given argument'''
    with driver.session() as session:

        attacked = session.run("""MATCH (a1:arg)-[:attack]->(a2:arg)
                                        WHERE $argument IN a1.sentences
                                        RETURN a2 as att
                                        """, argument=argument)
        
        return attacked.value()

def get_responses_attacked_by_argument(driver: Neo4jDriver, argument: str):
    '''Returns the reply nodes attacked by given argument'''
    with driver.session() as session:

        attacked = session.run("""MATCH (a1:arg)-[:attack]->(re:reply)
                                        WHERE $argument IN a1.sentences
                                        RETURN re as att""", argument=argument)
        
        return attacked.value()


def get_arguments_endorsed_by_argument(driver: Neo4jDriver, argument: str):
    '''Returns the argument nodes endorsed by given argument'''
    with driver.session() as session:

        endorsed = session.run("""MATCH (a1:arg)-[:endorse]->(a2:arg)
                                        WHERE $argument IN a1.sentences
                                        RETURN a2
                                        """, argument=argument)
        
        return endorsed.value()

def get_responses_endorsed_by_argument(driver: Neo4jDriver, argument: str):
    '''Returns the reply nodes endorsed by given argument'''
    with driver.session() as session:

        endorsed = session.run("""MATCH (a1:arg)-[:endorse]->(re:reply)
                                        WHERE $argument IN a1.sentences
                                        RETURN re""", argument=argument)
        
        return endorsed.value()

def get_node_containing_sentence(driver: Neo4jDriver, sentence: str):
    '''Return the node containing this sentence'''
    with driver.session() as session:

        node = session.run("""MATCH (n)
                                WHERE $s in n.sentences
                                RETURN n""")

        return node.value()

def get_responses(driver: Neo4jDriver):

    with driver.session() as session:

        responses = session.run("""MATCH (r:reply)
                                RETURN r""")

        return responses.value()