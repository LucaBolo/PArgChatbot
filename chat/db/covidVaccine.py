
import networkx as nx

class CovidVaccineGraph:

    def __init__(self) -> None:
        self.graph = nx.DiGraph()

    def create_nodes(self):
        self.graph.add_nodes_from([
            (
                "a1", {"class":"p", "question":"Are you celiac?", "sentences": ["I am celiac",
                                                        "I suffer from the celiac disease",
                                                        "I am afflicted with the celiac disease",
                                                        "I have the celiac disease",
                                                        "I recently found out to be celiac",
                                                        "I have suffered from celiac disease since birth"]
                }
            ),
            (
                "a2", {"class":"n", "question":"Are you celiac?", "sentences": ["I do not have the celiac disease",
                                                        "I am not celiac",
                                                        "I do not suffer from the celiac disease",
                                                        "I am not afflicted with the celiac disease"]
                }
            ),
            (
                "a3", {
                    "class":"n", "question":"Are you immunosuppressed?", "sentences": ["I am not immunosuppressed",
                                                        "I do not suffer from immunosuppression",
                                                        "I am not afflicted with immunosuppression"]
                }
            ),
            (
                "a4", {
                    "class":"p", "question":"Are you immunosuppressed?", "sentences": ["I am immunosuppressed",
                                                        "I suffer from immunosuppression",
                                                        "I am afflicted with immunosuppression",
                                                        "I do suffer from immunosuppression",
                                                        "I indeed suffer from immunosuppression",
                                                        "I recently found out to be immunosuppressed"]
                }
            ),
            (
                "a5", {
                    "class":"n", "question":"Do you have any drug allergy?", "sentences": ["I do not have any drug allergy",
                                                        "I do not suffer from drug allergies",
                                                        "I do not suffer from any drug allergy",
                                                        "I am not afflicted with any drug allergy",
                                                        "I do not have medication allergies",
                                                        "I do not have any medication allergy"]
                }
            ),
            (
                "a6", {
                    "class":"p", "question":"Do you have any drug allergy?", "sentences": ["I have a drug allergy",
                                                        "I do have a drug allergy",
                                                        "I have a serious drug allergy",
                                                        "I suffer from drug allergy",
                                                        "I am afflicted with drug allergies",
                                                        "I suffer from medication allergies"]
                }
            ),
            (
                "a7", {
                    "class":"n", "question":"Do you have bronchial asthma?", "sentences": ["I do not suffer from bronchial asthma",
                                                        "I don't have bronchial asthma",
                                                        "I've never had bronchial asthma",
                                                        "I am not afflicted with bronchial asthma"]
                }
            ),
            (
                "a8", {
                    "class":"p", "question":"Do you have bronchial asthma?", "sentences": ["I suffer from bronchial asthma",
                                                        "I have bronchial asthma",
                                                        "I am affected by bronchial asthma",
                                                        "I am afflicted with bronchial asthma"]
                }
            ),
            (
                "a9", {
                    "class":"p", "question":"Do you have diabetes?", "sentences": ["I suffer from diabetes",
                                                        "I am diabetic",
                                                        "I am affected by diabetes"]
                }
            ),
            (
                "a10", {
                    "class":"n", "question":"Do you have diabetes?", "sentences": ["I do not suffer from diabetes",
                                                        "I am not affected by diabetes",
                                                        "I am not diabetic",
                                                        "I don't have diabetes"]
                }
            ),
            (
                "a11", {
                    "class":"p", "question":"Are you allergic to latex?", "sentences": ["I suffer from latex allergy",
                                                        "I'm allergic to latex",
                                                        "I have a latex allergy",
                                                        "Latex causes me an allergic reaction"]
                }
            ),
            (
                "a12", {
                    "class":"n", "question":"Are you allergic to latex?", "sentences": ["I do not suffer from latex allergy",
                                                        "I'm not allergic to latex",
                                                        "I do not have a latex allergy",
                                                        "Latex does not cause me an allergic reaction",
                                                        "I have never had an allergic reaction with latex"]
                }
            ),
            (
                "a13", {
                    "class":"n", "question":"Do you suffer from mastocytosis?", "sentences": ["I do not suffer from mastocytosis",
                                                        "I am not afflicted with mastocystosis",
                                                        "I do not have mastocystosis",
                                                        "Mastocystosis is not an health concern for me"]
                }
            ),
            (
                "a14", {
                    "class":"p", "question":"Do you suffer from mastocytosis?", "sentences": ["I suffer from mastocytosis",
                                                        "I am afflicted with mastocystosis",
                                                        "I have a condition called mastocystosis"]
                }
            ),
            (
                "a15", {
                    "class":"p", "question":"Have you had anaphylactic reactions?", "sentences": ["I have experienced a serious anaphylaxis in the past",
                                                        "I have had an anaphylactic reaction in the past",
                                                        "I have already had an anaphylactic reaction before",
                                                        "I went into anaphylactic shock before"]
                }
            ),
            (
                "a16", {
                    "class":"n", "question":"Have you had anaphylactic reactions?", "sentences": ["I've never experienced a serious anaphylaxis",
                                                        "I've never had a serious anaphylactic reaction",
                                                        "I've never gone into anaphylactic shock before"]
                }
            ),
            (
                "r1", {
                    "sentence": ["Get vaccinated at any vaccine site. No special monitoring"]
                }
            ),
            (
                "r2", {
                    "sentence": ["Get vaccinated at any vaccine site. Monitoring for 60 minutes"]
                }
            ),
            (
                "r3", {
                    "sentence": ["Get vaccinated at the hospital"]
                }
            )

        ])

        return self.graph.number_of_nodes()

    def create_edges(self):
        # add argument and their negation
        for i1,i2 in zip(range(1,16,2), range(2,17,2)):
            self.graph.add_edge(f"a{i1}",f"a{i2}",type="attack")

        for i1,i2 in zip(range(2,17,2), range(1,16,2)):
            self.graph.add_edge(f"a{i1}",f"a{i2}",type="attack")

        
        self.graph.add_edges_from([
            (
                "a1", "r1", {"type":"endorse"}
            ),
            (
                "a2", "r1", {"type":"endorse"}
            ),
            (
                "a3", "r1", {"type":"endorse"}
            ),
            (
                "a4", "r1", {"type":"endorse"}
            ),
            (
                "a5", "r1", {"type":"endorse"}
            ),
            (
                "a7", "r1", {"type":"endorse"}
            ),
            (
                "a9", "r1", {"type":"endorse"}
            ),
            (
                "a10", "r1", {"type":"endorse"}
            ),
            (
                "a12", "r1", {"type":"endorse"}
            ),
            (
                "a13", "r1", {"type":"endorse"}
            ),
            (
                "a16", "r1", {"type":"endorse"}
            ),
            (
                "a6", "r1", {"type":"attack"}
            ),
            (
                "a8", "r1", {"type":"attack"}
            ),
            (
                "a11", "r1", {"type":"attack"}
            ),
            (
                "a14", "r1", {"type":"attack"}
            ),
            (
                "a15", "r1", {"type":"attack"}
            ),
            (
                "a6", "r2", {"type":"endorse"}
            ),
            (
                "a11", "r2", {"type":"endorse"}
            ),
            (
                "a14", "r2", {"type":"endorse"}
            ),
            (
                "a8", "r2", {"type":"attack"}
            ),
            (
                "a15", "r2", {"type":"attack"}
            ),
            (
                "a8", "r3", {"type":"endorse"}
            ),
            (
                "a15", "r3", {"type":"endorse"}
            ),
        ])
        
        return self.graph.number_of_edges()    



if __name__=='__main__':

    g = CovidVaccineGraph()

    print(g.create_nodes())
    print(g.create_edges())

    for u,v, d in g.graph.edges.data(nbunch=[f"a{i}" for i in range(1,17)]):
        print(u,v,d)
