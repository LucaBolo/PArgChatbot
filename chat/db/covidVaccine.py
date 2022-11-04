from neo4j import GraphDatabase


class CovidVaccineGraph:

    def __init__(self, uri, user, password) -> None:
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    @staticmethod
    def create_nodes(tx):
        
        result = tx.run('''CREATE (N1:arg {id:"n1", question:"Are you celiac?", sentences: ["I am celiac",
                                                        "I suffer from the celiac disease",
                                                        "I am afflicted with the celiac disease",
                                                        "I have the celiac disease",
                                                        "I recently found out to be celiac",
                                                        "I have suffered from celiac disease since birth"]})-[n1n2:attack]->
                                    (N2:arg {id:"n2", question:"Are you celiac?", sentences: ["I do not have the celiac disease",
                                                        "I am not celiac",
                                                        "I do not suffer from the celiac disease",
                                                        "I am not afflicted with the celiac disease"]}),
                                    (N3:arg {id:"n3", question:"Are you immunosuppressed?", sentences: ["I am not immunosuppressed",
                                                        "I do not suffer from immunosuppression",
                                                        "I am not afflicted with immunosuppression"]})-[n3n4:attack]->
                                    (N4:arg {id:"n4", question:"Are you immunosuppressed?", sentences: ["I am immunosuppressed",
                                                        "I suffer from immunosuppression",
                                                        "I am afflicted with immunosuppression",
                                                        "I do suffer from immunosuppression",
                                                        "I indeed suffer from immunosuppression",
                                                        "I recently found out to be immunosuppressed"]}),
                                    (N5:arg {id:"n5", question:"Do you have any drug allergy?", sentences: ["I do not have any drug allergy",
                                                        "I do not suffer from drug allergies",
                                                        "I do not suffer from any drug allergy",
                                                        "I am not afflicted with any drug allergy",
                                                        "I do not have medication allergies",
                                                        "I do not have any medication allergy"]})-[n5n6:attack]->
                                    (N6:arg {id:"n6", question:"Do you have any drug allergy?", sentences: ["I have a drug allergy",
                                                        "I do have a drug allergy",
                                                        "I have a serious drug allergy",
                                                        "I suffer from drug allergy",
                                                        "I am afflicted with drug allergies",
                                                        "I suffer from medication allergies"]}),
                                    (N7:arg {id:"n7", question:"Do you have bronchial asthma?", sentences: ["I do not suffer from bronchial asthma",
                                                        "I don't have bronchial asthma",
                                                        "I've never had bronchial asthma",
                                                        "I am not afflicted with bronchial asthma"]})-[n7n8:attack]->
                                    (N8:arg {id:"n8", question:"Do you have bronchial asthma?", sentences: ["I suffer from bronchial asthma",
                                                        "I have bronchial asthma",
                                                        "I am affected by bronchial asthma",
                                                        "I am afflicted with bronchial asthma"]}),
                                    (N9:arg {id:"n9", question:"Do you have diabetes?", sentences: ["I suffer from diabetes",
                                                        "I am diabetic",
                                                        "I am affected by diabetes"]})-[n9n10:attack]->
                                    (N10:arg {id:"n10", question:"Do you have diabetes?", sentences: ["I do not suffer from diabetes",
                                                        "I am not affected by diabetes",
                                                        "I am not diabetic",
                                                        "I don't have diabetes"]}),
                                    (N11:arg {id:"n11", question:"Are you allergic to latex?", sentences: ["I suffer from latex allergy",
                                                        "I'm allergic to latex",
                                                        "I have a latex allergy",
                                                        "Latex causes me an allergic reaction"]})-[n11n12:attack]->
                                    (N12:arg {id:"n12", question:"Are you allergic to latex?", sentences: ["I do not suffer from latex allergy",
                                                        "I'm not allergic to latex",
                                                        "I do not have a latex allergy",
                                                        "Latex does not cause me an allergic reaction",
                                                        "I have never had an allergic reaction with latex"]}),
                                    (N13:arg {id:"n13", question:"Do you suffer from mastocytosis?", sentences: ["I do not suffer from mastocytosis",
                                                        "I am not afflicted with mastocystosis",
                                                        "I do not have mastocystosis",
                                                        "Mastocystosis is not an health concern for me"]})-[n13n14:attack]->
                                    (N14:arg {id:"n14", question:"Do you suffer from mastocytosis?", sentences: ["I suffer from mastocytosis",
                                                        "I am afflicted with mastocystosis",
                                                        "I have a condition called mastocystosis"]}),
                                    (N15:arg {id:"n15", question:"Have you had anaphylactic reactions?", sentences: ["I have experienced a serious anaphylaxis in the past",
                                                        "I have had an anaphylactic reaction in the past",
                                                        "I have already had an anaphylactic reaction before",
                                                        "I went into anaphylactic shock before"]})-[n15n16:attack]->
                                    (N16:arg {id:"n16", question:"Have you had anaphylactic reactions?", sentences: ["I've never experienced a serious anaphylaxis",
                                                        "I've never had a serious anaphylactic reaction",
                                                        "I've never gone into anaphylactic shock before"]}),
                                    (R1:reply {id:"r1", sentence: ["Get vaccinated at any vaccine site. No special monitoring"]}),
                                    (R2:reply {id:"r2", sentence: ["Get vaccinated at any vaccine site. Monitoring for 60 minutes"]}),
                                    (R3:reply {id:"r3", sentence: ["Get vaccinated at the hospital"]})''')
        records = result.value()
        return len(records)

    @staticmethod
    def create_edges(tx, node1_id, node1_label, node2_id, node2_label, reltype):
        tx.run(f'''
                MATCH (n1:{node1_label}), (n2:{node2_label})
                WHERE n1.id = $node1 AND n2.id = $node2
                CREATE (n1)-[{node1_id}{node2_id}:{reltype}]->(n2)
                ''', node1=node1_id, node2=node2_id)
        
        return 0

    @staticmethod
    def delete_nodes(tx):
        result = tx.run("MATCH (nodes) DETACH DELETE nodes")
        records = result.value()
        assert len(records) == 0
        return len(records)


    @staticmethod
    def read_nodes(tx):

        nodes = tx.run("MATCH (nodes:arg) return nodes")
        return nodes.value()

    @staticmethod
    def read_edges(tx):

        edges = tx.run("MATCH (nodes1)-[]->(nodes2) return nodes1, nodes2")
        return edges.value()

    def populate_db(self):
        with self.driver.session() as session:
            #session.execute_read()
            session.write_transaction(self.create_nodes)
            session.write_transaction(self.create_edges, "n2", "arg", "n1", "arg", "attack")
            session.write_transaction(self.create_edges, "n1", "arg", "r1", "reply", "endorse")
            session.write_transaction(self.create_edges, "n2", "arg", "r1", "reply", "endorse")
            session.write_transaction(self.create_edges, "n10", "arg", "n9", "arg", "attack")
            session.write_transaction(self.create_edges, "n9", "arg", "r1", "reply", "endorse")
            session.write_transaction(self.create_edges, "n10", "arg", "r1", "reply", "endorse")
            session.write_transaction(self.create_edges, "n4", "arg", "n3", "arg", "attack")
            session.write_transaction(self.create_edges, "n3", "arg", "r1", "reply", "endorse")
            session.write_transaction(self.create_edges, "n4", "arg", "r1", "reply", "endorse")
            session.write_transaction(self.create_edges, "n8", "arg", "n7", "arg", "attack")
            session.write_transaction(self.create_edges, "n7", "arg", "r1", "reply", "endorse")
            session.write_transaction(self.create_edges, "n8", "arg", "r1", "reply", "attack")
            session.write_transaction(self.create_edges, "n8", "arg", "r2", "reply", "attack")
            session.write_transaction(self.create_edges, "n8", "arg", "r3", "reply", "endorse")
            session.write_transaction(self.create_edges, "n16", "arg", "n15", "arg", "attack")
            session.write_transaction(self.create_edges, "n16", "arg", "r1", "reply", "endorse")
            session.write_transaction(self.create_edges, "n15", "arg", "r1", "reply", "attack")
            session.write_transaction(self.create_edges, "n15", "arg", "r2", "reply", "attack")
            session.write_transaction(self.create_edges, "n15", "arg", "r3", "reply", "endorse")
            session.write_transaction(self.create_edges, "n14", "arg", "n13", "arg", "attack")
            session.write_transaction(self.create_edges, "n14", "arg", "r1", "reply", "attack")
            session.write_transaction(self.create_edges, "n14", "arg", "r2", "reply", "endorse")
            session.write_transaction(self.create_edges, "n13", "arg", "r1", "reply", "endorse")
            session.write_transaction(self.create_edges, "n6", "arg", "n5", "arg", "attack")
            session.write_transaction(self.create_edges, "n6", "arg", "r1", "reply", "attack")
            session.write_transaction(self.create_edges, "n6", "arg", "r2", "reply", "endorse")
            session.write_transaction(self.create_edges, "n5", "arg", "r1", "reply", "endorse")
            session.write_transaction(self.create_edges, "n12", "arg", "n11", "arg", "attack")
            session.write_transaction(self.create_edges, "n12", "arg", "r1", "reply", "endorse")
            session.write_transaction(self.create_edges, "n11", "arg", "r1", "reply", "attack")
            session.write_transaction(self.create_edges, "n11", "arg", "r2", "reply", "endorse")
            #nodes = session.execute_read(self.read_nodes)
            
    
    
    def reset_db(self):
        with self.driver.session() as session:
            n = session.write_transaction(self.delete_nodes)
            print(n)

    def read_db(self):
        with self.driver.session() as session:
            nodes = session.execute_read(self.read_nodes)
            print(len(nodes))
            edges = session.execute_read(self.read_edges)
            print(len(edges))

    def close(self):
        self.driver.close()


if __name__=='__main__':

    g = CovidVaccineGraph("neo4j://localhost:7687", "neo4j", "password")

    g.populate_db()
    g.close()
