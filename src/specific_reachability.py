#!/usr/bin/env python3
"""reachability inference for individual specs"""

import os
import sys
from owlready2 import get_ontology, default_world
import rdflib
import executequery as xq

ONTOFILE = "logistics-onto.owl"
IRI = "http://example.org/logistics-onto.owl"
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

def run_complex_query(ontofile, part1, part2, part3, spec):
    """create query for feasibility check of a spec"""
    myfile = open(PREFIXES, "r")
    query = myfile.read()
    myfile.close()
    for part in [part1, part2, part3]:
        myfile = open(part, "r")
        query += myfile.read()
        myfile.close()
        if not part == part3:
            query += spec
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

def remove_relations(ontofile, query_body):
    """remove existing specifically_connected_to relations"""
    myfile = open(PREFIXES, "r")
    query = myfile.read()
    myfile.close()
    myfile = open(query_body, "r")
    query += myfile.read()
    myfile.close()
    onto = get_ontology(IRI).load()
    graph = default_world.as_rdflib_graph()
    graph.update(query)
    onto.save(file=ontofile)

def insert_relations(specific_relations):
    """insert connected_to relations into onto"""
    onto = get_ontology(IRI).load()
    with onto:
        for i in specific_relations:
            onto[str(i[0]).split('.')[-1]].specifically_connected_to.\
                                           append(onto[str(i[1]).split('.')[-1]])
    onto.save(file=ONTOFILE)

def specific_feedback(infeasible_features):
    """return feedback which features cannot be realized"""
    for i in infeasible_features:
        if not i[1]:
            print(i[0], " - infeasible - no available resource can realize this feature")
        else:
            print(i[0], " - infeasible - no transport connection to resource that can realize ", i[1])

if __name__ == "__main__":
    for spec in get_spec_instances(ONTOFILE):
        print("feasibility feedback for " + spec)
        remove_relations(ONTOFILE, QUERY_DELETE)
        insert_relations(run_query(ONTOFILE, QUERY))
        specific_feedback(run_complex_query(ONTOFILE, QUERY_FEATS_1, QUERY_FEATS_2,\
                                            QUERY_FEATS_3, spec))
