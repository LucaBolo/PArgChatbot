from ast import arg
from neo4j import GraphDatabase

class ArgGraphDb:

    def __init__(self, uri, user, password) -> None:
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    @staticmethod
    def create_nodes(tx):
        
        result = tx.run('''CREATE (N1:arg {sentences: ["I am celiac",
                                                        "I suffer from the celiac disease",
                                                        "I am afflicted with the celiac disease",
                                                        "I have the celiac disease",
                                                        "I recently found out to be celiac",
                                                        "I have suffered from celiac disease since birth"]}),
                                    (N2:arg {sentences: ["I do not have the celiac disease",
                                                        "I am not celiac",
                                                        "I do not suffer from the celiac disease",
                                                        "I am not afflicted with the celiac disease"]}),
                                    (N3:arg {sentences: ["I am not immunosuppressed",
                                                        "I do not suffer from immunosuppression",
                                                        "I am not afflicted with immunosuppression"]}),
                                    (N4:arg {sentences: ["I am immunosuppressed",
                                                        "I suffer from immunosuppression",
                                                        "I am afflicted with immunosuppression",
                                                        "I do suffer from immunosuppression",
                                                        "I indeed suffer from immunosuppression",
                                                        "I recently found out to be immunosuppressed"]}),
                                    (N5:arg {sentences: ["I do not have any drug allergy",
                                                        "I do not suffer from drug allergies",
                                                        "I do not suffer from any drug allergy",
                                                        "I am not afflicted with any drug allergy",
                                                        "I do not have medication allergies",
                                                        "I do not have any medication allergy"]}),
                                    (N6:arg {sentences: ["I have a drug allergy",
                                                        "I do have a drug allergy",
                                                        "I have a serious drug allergy",
                                                        "I suffer from drug allergy",
                                                        "I am afflicted with drug allergies",
                                                        "I suffer from medication allergies"]}),
                                    (N7:arg {sentences: ["I do not suffer from bronchial asthma",
                                                        "I don't have bronchial asthma",
                                                        "I've never had bronchial asthma",
                                                        "I am not afflicted with bronchial asthma"]}),
                                    (N8:arg {sentences: ["I suffer from bronchial asthma",
                                                        "I have bronchial asthma",
                                                        "I am affected by bronchial asthma",
                                                        "I am afflicted with bronchial asthma"]}),
                                    (N9:arg {sentences: ["I suffer from diabetes",
                                                        "I am diabetic",
                                                        "I am affected by diabetes"]}),
                                    (N10:arg {sentences: ["I do not suffer from diabetes",
                                                        "I am not affected by diabetes",
                                                        "I am not diabetic",
                                                        "I don't have diabetes"]}),
                                    (N11:arg {sentences: ["I suffer from latex allergy",
                                                        "I'm allergic to latex",
                                                        "I have a latex allergy",
                                                        "Latex causes me an allergic reaction"]}),
                                    (N12:arg {sentences: ["I do not suffer from latex allergy",
                                                        "I'm not allergic to latex",
                                                        "I do not have a latex allergy",
                                                        "Latex does not cause me an allergic reaction",
                                                        "I have never had an allergic reaction with latex"]}),
                                    (N13:arg {sentences: ["I do not suffer from mastocytosis",
                                                        "I am not afflicted with mastocystosis",
                                                        "I do not have mastocystosis",
                                                        "Mastocystosis is not an health concern for me"]}),
                                    (N14:arg {sentences: ["I suffer from mastocytosis",
                                                        "I am afflicted with mastocystosis",
                                                        "I have a condition called mastocystosis"]}),
                                    (N15:arg {sentences: ["I have experienced a serious anaphylaxis in the past",
                                                        "I have had an anaphylactic reaction in the past",
                                                        "I have already had an anaphylactic reaction before",
                                                        "I went into anaphylactic shock before"]}),
                                    (N16:arg {sentences: ["I've never experienced a serious anaphylaxis",
                                                        "I've never had a serious anaphylactic reaction",
                                                        "I've never gone into anaphylactic shock before"]}),
                                    (R1:reply {sentence: "Get vaccinated at any vaccine site. No special monitoring"}),
                                    (R2:reply {sentence: "Get vaccinated at any vaccine site. Monitoring for 60 minutes"}),
                                    (R3:reply {sentence: "Get vaccinated at the hospital"})''')
        records = result.value()
        return len(records)

    @staticmethod
    def delete_nodes(tx):
        result = tx.run("MATCH (nodes) DELETE nodes")
        records = result.value()
        assert len(records) == 0
        return len(records)

    @staticmethod
    def read_nodes(tx):

        nodes = tx.run("MATCH (nodes) return nodes")
        return nodes.value()

    def populate_db(self):
        with self.driver.session() as session:
            #session.execute_read()
            # = session.write_transaction(self.create_nodes)
            #print(n)
            nodes = session.execute_read(self.read_nodes)
            print(len(nodes))
    
    
    def reset_db(self):
        with self.driver.session() as session:
            n = session.write_transaction(self.delete_nodes)
            print(n)

    def close(self):
        self.driver.close()

if __name__ == '__main__':
    g = ArgGraphDb("neo4j://localhost:7687", "neo4j", "password")
    g.populate_db()
    g.close()