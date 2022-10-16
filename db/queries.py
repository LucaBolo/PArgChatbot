from neo4j import Neo4jDriver


def get_sentences_attacking_response(driver: Neo4jDriver, response: str):
    '''Returns the attacking arguments to this response'''
    with driver.session() as session:

        attacking_args = session.run("""MATCH (a:arg)-[:attack]->(re:reply) 
                                        WHERE $response IN re.sentence
                                        RETURN a.sentences""", response=response)
        # WHERE $response IN a.sentences 
        # WITH COLLECT(DISTINCT a.sentences) as kb
        # [s in kb WHERE s IN  $status] as attacking_args
        return [arg_sentence for node in attacking_args.value() for arg_sentence in node]


def get_sentences_attacking_argument(driver: Neo4jDriver, argument: str):
    '''Returns the attacking arguments to this argument,
    usually just its negated'''
    with driver.session() as session:

        attacking_args = session.run("""MATCH (a1:arg)-[:attack]->(a2:arg) 
                                        WHERE $argument IN a2.sentences
                                        RETURN a1.sentences""", argument=argument)
        
        return [arg_sentence for node in attacking_args.value() for arg_sentence in node]


def get_sentences_endorsing_response(driver: Neo4jDriver, response: str):
    with driver.session() as session:

        endorsing_args = session.run("""MATCH (a:arg)-[:endorse]->(re:reply) 
                                        WHERE $response IN re.sentence
                                        RETURN a.sentences""", response=response)
        
        return [arg_sentence for node in endorsing_args.value() for arg_sentence in node]

def get_sentences_attacked_by_argument(driver: Neo4jDriver, argument: str):
    with driver.session() as session:

        attacked = session.run("""MATCH (a1:arg)-[:attack]->(a2:arg)
                                        WHERE $argument IN a1.sentences
                                        RETURN a2.sentences as att
                                        UNION
                                        MATCH (a1:arg)-[:attack]->(re:reply)
                                        WHERE $argument IN a1.sentences
                                        RETURN re.sentence as att""", argument=argument)
        
        return [arg_sentence for node in attacked.value() for arg_sentence in node]


def get_sentences_endorsed_by_argument(driver: Neo4jDriver, argument: str):
    with driver.session() as session:

        endorsed = session.run("""MATCH (a1:arg)-[:endorse]->(a2:arg)
                                        WHERE $argument IN a1.sentences
                                        RETURN a2.sentences as att
                                        UNION
                                        MATCH (a1:arg)-[:endorse]->(re:reply)
                                        WHERE $argument IN a1.sentences
                                        RETURN re.sentence as att""", argument=argument)
        
        return [arg_sentence for node in endorsed.value() for arg_sentence in node]