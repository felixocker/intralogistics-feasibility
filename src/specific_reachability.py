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

def run_query(ontofile, query_body):
    """build query and run on ontofile"""
    myfile = open(PREFIXES, "r")
    query = myfile.read()
    myfile.close()
    myfile = open(query_body, "r")
    query += myfile.read()
    myfile.close()
    return xq.executequery(ontofile, query)

def insert_relations(specific_relations):
    """insert connected_to relations into onto"""
    onto = get_ontology(IRI).load()
    with onto:
        for i in specific_relations:
            onto[str(i[0]).split('.')[-1]].specifically_connected_to.append(onto[str(i[1]).split('.')[-1]])
    onto.save(file=ONTOFILE)

if __name__ == "__main__":
    insert_relations(run_query(ONTOFILE, QUERY))
