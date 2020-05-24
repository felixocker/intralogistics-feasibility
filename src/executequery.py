#!/usr/bin/env python3
"""module loads ontology, runs SPARQL query, and returns results as list"""

from owlready2 import get_ontology, default_world

def executequery(pathtoonto, query):
    """load ontology, query it, and return results as list"""
    onto = get_ontology(pathtoonto).load()
    graph = default_world.as_rdflib_graph()
    return list(graph.query_owlready(query))
