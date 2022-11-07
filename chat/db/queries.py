from neo4j import Neo4jDriver
from neo4j.graph import Node

def get_arguments_attacking_reply(driver: Neo4jDriver, reply: Node):
    '''Returns the attacking arguments to this reply, flattened'''
    with driver.session() as session:
        
        node_id = reply.get("id")
        attacking_args = session.run("""MATCH (a:arg)-[:attack]->(re:reply) 
                                        WHERE $node_id = re.id
                                        RETURN a""", node_id=node_id)
        # WHERE $reply IN a.sentences 
        # WITH COLLECT(DISTINCT a.sentences) as kb
        # [s in kb WHERE s IN  $status] as attacking_args
        return attacking_args.value()


def get_arguments_attacking_argument(driver: Neo4jDriver, argument: Node):
    '''Returns the attacking arguments to this argument,
    usually just its negated, flattened'''
    with driver.session() as session:

        node_id = argument.get("id")
        attacking_args = session.run("""MATCH (a1:arg)-[:attack]->(a2:arg) 
                                        WHERE $node_id IN a2.id
                                        RETURN a1""", node_id=node_id)
        
        return attacking_args.value()


def get_arguments_endorsing_reply(driver: Neo4jDriver, reply: Node):
    '''Returns the argument nodes that endorse this reply, flattened'''
    with driver.session() as session:
        
        node_id = reply.get("id")
        endorsing_args = session.run("""MATCH (a:arg)-[:endorse]->(re:reply) 
                                        WHERE $node_id IN re.id
                                        RETURN a""", node_id=node_id)
        
        return endorsing_args.value()

def get_arguments_attacked_by_argument(driver: Neo4jDriver, argument: Node):
    '''Returns the argument nodes attacked by given argument'''
    with driver.session() as session:
        
        node_id = argument.get("id")
        attacked = session.run("""MATCH (a1:arg)-[:attack]->(a2:arg)
                                        WHERE $node_id IN a1.id
                                        RETURN a2 as att
                                        """, node_id=node_id)
        
        return attacked.value()

def get_replies_attacked_by_argument(driver: Neo4jDriver, argument: Node):
    '''Returns the reply nodes attacked by given argument'''
    with driver.session() as session:
        
        node_id = argument.get("id")
        attacked = session.run("""MATCH (a1:arg)-[:attack]->(re:reply)
                                        WHERE $node_id IN a1.id
                                        RETURN re as att""", node_id=node_id)
        
        return attacked.value()


def get_arguments_endorsed_by_argument(driver: Neo4jDriver, argument: Node):
    '''Returns the argument nodes endorsed by given argument'''
    with driver.session() as session:
        
        node_id = argument.get("id")
        endorsed = session.run("""MATCH (a1:arg)-[:endorse]->(a2:arg)
                                        WHERE $node_id IN a1.id
                                        RETURN a2
                                        """, node_id=node_id)
        
        return endorsed.value()

def get_replies_endorsed_by_argument(driver: Neo4jDriver, argument: Node):
    '''Returns the reply nodes endorsed by given argument'''
    with driver.session() as session:
        
        node_id = argument.get("id")
        endorsed = session.run("""MATCH (a1:arg)-[:endorse]->(re:reply)
                                        WHERE $node_id IN a1.id
                                        RETURN re""", node_id=node_id)
        
        return endorsed.value()

def get_node_containing_sentence(driver: Neo4jDriver, sentence: str):
    '''Return the node containing this sentence.
    It assumes only a single node contains the specific sentence'''
    with driver.session() as session:

        
        node = session.run("""MATCH (n)
                                WHERE $sentence in n.sentences
                                RETURN n""", sentence=sentence)

        return node.value()[0]

def get_replies(driver: Neo4jDriver):

    with driver.session() as session:

        replies = session.run("""MATCH (r:reply)
                                RETURN r""")

        return replies.value()

def get_questions(driver: Neo4jDriver):

    with driver.session() as session:

        questions = session.run("""MATCH (a:arg)
                                    RETURN a.question""")

        return questions.value()

def get_sentences(driver: Neo4jDriver):

    with driver.session() as session:

        sentences = session.run("""MATCH (a:arg)
                                    RETURN a.sentences""")

        return sentences.value()

def get_question_of_node_containing_sentence(driver: Neo4jDriver, sentence: str):
    with driver.session() as session:

        
        node = session.run("""MATCH (n)
                                WHERE $sentence in n.sentences
                                RETURN n.question""", sentence=sentence)

        return node.value()[0]