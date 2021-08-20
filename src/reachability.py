#!/usr/bin/env python3
"""inference engine for reachability analysis"""

import sys
from itertools import product
from owlready2 import get_ontology
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon
import executequery as xq

PREFIXES = "../queries/prefixes.sparql"
QUERY_LOG = "../queries/find_transport_resources.sparql"
QUERY_NON_LOG = "../queries/find_non_transport_resources.sparql"

ACCEPTED_DEVIATION = 1e-8

def run_query(ontofile, query_body):
    """build query and run on ontofile"""
    myfile = open(PREFIXES, "r")
    query = myfile.read()
    myfile.close()
    myfile = open(query_body, "r")
    query += myfile.read()
    myfile.close()
    return xq.executequery(ontofile, query)

def point_trafo(elem, table, identifier):
    """create shapely point object from coordinates"""
    coordinates = [None, None]
    coordinates[0] = elem[4 + identifier]
    coordinates[1] = elem[5 + identifier]
    return Point(coordinates)

def line_trafo(elem, table, identifier):
    """create shapely line object from coordinates"""
    coordinates = [[None, None], [None, None]]
    for e in table:
        if e[2 + identifier] == elem[2 + identifier] and not coordinates[0][0]:
            coordinates[0][0] = e[4 + identifier]
            coordinates[0][1] = e[5 + identifier]
        elif e[2 + identifier] == elem[2 + identifier]:
            coordinates[1][0] = e[4 + identifier]
            coordinates[1][1] = e[5 + identifier]
    return LineString([[coordinates[0][0], coordinates[0][1]],
                       [coordinates[1][0], coordinates[1][1]]])

def circle_trafo(elem, table, identifier):
    """create shapely circle object from coordinates"""
    coordinates = [[None, None], None]
    for e in table:
        if e[2 + identifier] == elem[2 + identifier] and e[3 + identifier]:
            coordinates[0][0] = e[4 + identifier]
            coordinates[0][1] = e[5 + identifier]
        if e[2 + identifier] == elem[2 + identifier] and e[6 + identifier]:
            coordinates[1] = e[7 + identifier]
    return Point(coordinates[0]).buffer(coordinates[1])

def polygon_trafo(elem, table, identifier):
    """create shapely polygon object from coordinates"""
    coordinates = []
    point = [None, None]
    # add first point, randomly, depending on query results
    for counter in range(len(table)):
        if table[counter][2 + identifier] == elem[2 + identifier]:
            point[0] = table[counter][4 + identifier]
            point[1] = table[counter][5 + identifier]
            coordinates.append(point)
            break
    # add neighbors
    coordinates = find_neighbors(table, identifier, elem[3 + identifier],
                                 elem[3 + identifier], elem[3 + identifier], coordinates)
    return Polygon(coordinates)

def find_neighbors(table, identifier, current, prev, start, neighbors):
    """create ordered list of polygon's points"""
    for elem in table:
        if elem[-1] == current and elem[3 + identifier] != start and\
           elem[3 + identifier] != prev:
            point = [None, None]
            prev = current
            current = elem[3 + identifier]
            point[0] = elem[4 + identifier]
            point[1] = elem[5 + identifier]
            neighbors.append(point)
            find_neighbors(table, identifier, current, prev, start, neighbors)
            break # only do this for one neighbor of first point, which one does not matter
    return neighbors

def process_query_results(ontofile, query_t, query_nt):
    """process results of transport query for location check modules"""
    transp_table = run_query(ontofile, query_t)
    transp_res = []
    non_transp_table = run_query(ontofile, query_nt)
    non_transp_res = []
    # style: resource, type {sink, source, location}, shapely object
    # to be interpreted as: "resource has area as sink/ source / location"
    funcs = {"point": point_trafo,
             "line": line_trafo,
             "circle": circle_trafo,
             "polygon": polygon_trafo}
    identifier = 1
    for elem in range(len(transp_table)): # avoid duplicates
        if not True in [transp_table[elem][3] == pelem[3] for pelem in transp_table[:elem]]:
            # to be interpreted as: blank[0] has as blank[1] the area blank[2]
            blank = [None, None, None]
# TODO: check if there are cases, where both sink and source are set?
            if transp_table[elem][0]:
                blank[0] = transp_table[elem][0]
                blank[1] = "source" # resource is sink, but the area is the source
            if transp_table[elem][1]:
                blank[0] = transp_table[elem][1]
                blank[1] = "sink" # resource is source, but the area is the sink
            try:
                blank[2] = funcs[str(transp_table[elem][2]).split(".")[-1]]\
                                (transp_table[elem], transp_table, identifier)
            except KeyError:
                print("unknown function type")
                sys.exit(1)
            transp_res.append(blank)
    identifier = 0
    for elem in range(len(non_transp_table)):
        if not True in [non_transp_table[elem][2] for pelem in non_transp_table[:elem]]:
            blank = [None, None, None]
            blank[0] = non_transp_table[elem][0]
            blank[1] = "location"
            try:
                blank[2] = funcs[str(non_transp_table[elem][1]).split(".")[-1]]\
                                (non_transp_table[elem], non_transp_table,
                                 identifier)
            except KeyError:
                print("unknown function type")
                sys.exit(1)
            non_transp_res.append(blank)
    return [transp_res, non_transp_res]

def insert_relations(geometry_info, iri, ontofile):
    """insert connected_to relations into onto"""
    transp_res = geometry_info[0]
    non_transp_res = geometry_info[1]
    sources = [source for source in transp_res if source[1] == "source"]
    sinks = [sink for sink in transp_res if sink[1] == "sink"]
    connections = []
    connections.extend(check_overlap(sinks, sources))
    connections.extend(check_overlap(sinks, non_transp_res))
    connections.extend(check_overlap(non_transp_res, sources))
    # remove duplicates
    connections = list(set(map(lambda i: tuple(i), connections)))
    onto = get_ontology(iri).load()
    with onto:
        for i in connections:
            onto[i[0].split('.')[-1]].connected_to.append(onto[i[1].split('.')[-1]])
    onto.save(file=ontofile)

def check_overlap(res_a, res_b):
    """check if two areas/ lines/ points overlap"""
    # NOTE: use distance, otherwise numerical issues, especially w circles
    connections = []
    for i in list(product(res_a, res_b)):
        coord1 = i[0][2]
        coord2 = i[1][2]
        if i[0][0] != i[1][0]:
            if isinstance(coord1, Point) and isinstance(coord2, Point) and\
               list(coord1.coords) == list(coord2.coords) or\
               isinstance(coord1, Point) and not isinstance(coord2, Point) and\
               coord2.distance(coord1) < ACCEPTED_DEVIATION or\
               not isinstance(coord1, Point) and isinstance(coord2, Point) and\
               coord1.distance(coord2) < ACCEPTED_DEVIATION or\
               not isinstance(coord1, Point) and not isinstance(coord2, Point) and\
               coord1.intersects(coord2):
                connections.append([str(i[0][0]), str(i[1][0])])
    return connections

def infer_reachability(iri, ontofile):
    """infer reachability and save new facts to original onto"""
    query_results = process_query_results(ontofile, QUERY_LOG, QUERY_NON_LOG)
    insert_relations(query_results, iri, ontofile)

if __name__ == "__main__":
    iri = "http://example.org/logistics-onto.owl"
    ontofile = "logistics-onto.owl"
    infer_reachability(iri, ontofile)
