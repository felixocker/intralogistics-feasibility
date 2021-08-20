#!/usr/bin/env python3
"""reachability inference for individual specs"""

from owlready2 import get_ontology, default_world
import executequery as xq

PREFIXES = "../queries/prefixes.sparql"
QUERY = "../queries/find_viable_transport_resources.sparql"
QUERY_FEATS = "../queries/feature_feasibility.sparql"
QUERY_FEATS_1 = "../queries/feature_feasibility_pt1.sparql"
QUERY_FEATS_2 = "../queries/feature_feasibility_pt2.sparql"
QUERY_FEATS_3 = "../queries/feature_feasibility_pt3.sparql"
QUERY_DELETE = "../queries/delete_connections.sparql"
QUERY_SPECS = "../queries/find_specs.sparql"

def get_spec_instances(ontofile):
    """get all top-level specs"""
    spec_names = []
    specs = run_query(ontofile, QUERY_SPECS)
    for elem in specs:
        spec_names.append(":" + str(elem[0]).split('.')[-1])
    return spec_names

def run_complex_query(ontofile, part1, part2, part3, specif):
    """create query for feasibility check of a specification"""
    myfile = open(PREFIXES, "r")
    query = myfile.read()
    myfile.close()
    for part in [part1, part2, part3]:
        myfile = open(part, "r")
        query += myfile.read()
        myfile.close()
        if not part == part3:
            query += specif
    return xq.executequery(ontofile, query)

def run_query(ontofile, query_body):
    """build query and run on ontofile"""
    myfile = open(PREFIXES, "r")
    query = myfile.read()
    myfile.close()
    myfile = open(query_body, "r")
    query += myfile.read()
    myfile.close()
    return xq.executequery(ontofile, query)

def remove_relations(iri, ontofile, query_body):
    """remove existing specifically_connected_to relations"""
    myfile = open(PREFIXES, "r")
    query = myfile.read()
    myfile.close()
    myfile = open(query_body, "r")
    query += myfile.read()
    myfile.close()
    onto = get_ontology(iri).load()
    graph = default_world.as_rdflib_graph()
    graph.update(query)
    onto.save(file=ontofile)

def insert_relations(specific_relations, iri, ontofile):
    """insert connected_to relations into onto"""
    onto = get_ontology(iri).load()
    with onto:
        for i in specific_relations:
            onto[str(i[0]).split('.')[-1]].specifically_connected_to.\
                                           append(onto[str(i[1]).split('.')[-1]])
    onto.save(file=ontofile)

def specific_feedback(infeasible_features):
    """return feedback which features cannot be realized"""
    msg1 = "- infeasible - no available resource can realize this feature"
    msg2 = "- infeasible - no transport connection to resource that can realize"
    if not infeasible_features:
        print("no infeasible features")
    else:
        for i in infeasible_features:
            if not i[1]:
                print(i[0], msg1)
            else:
                print(i[0], msg2, i[1])

def check_feasibility(iri, ontofile):
    """check intralogistics feasibility under consideration of product spec"""
    for spec in get_spec_instances(ontofile):
        print("feasibility feedback for " + spec)
        remove_relations(iri, ontofile, QUERY_DELETE)
        insert_relations(run_query(ontofile, QUERY), iri, ontofile)
        specific_feedback(run_complex_query(ontofile, QUERY_FEATS_1, QUERY_FEATS_2,\
                                            QUERY_FEATS_3, spec))

if __name__ == "__main__":
    iri = "http://example.org/logistics-onto.owl"
    ontofile = "logistics-onto.owl"
    check_feasibility(iri, ontofile)
