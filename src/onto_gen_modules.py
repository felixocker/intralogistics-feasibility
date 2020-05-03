#!/usr/bin/env python3
"""modules for ontology generation from csv and json files"""

import csv
import json
from owlready2 import get_ontology, types

def get_csv_data(input_file):
    """read data from csv and return as nested list"""
    with open(input_file, newline='') as csvfile:
        csv_data = list(csv.reader(csvfile, delimiter=','))
    return csv_data

def get_json_data(input_file):
    """read data from json and return as nested list"""
    with open(input_file) as jsonfile:
        json_data = json.load(jsonfile)
    return json_data

def dynamically_create_classes(iri, output, input_list):
    """create classes from list"""
    onto = get_ontology(iri).load()
    with onto:
        for i in input_list[1:]:
            my_class = types.new_class(i[0], (getattr(onto, i[1]),))
            if i[2]:
                my_class.comment.append(i[2])
    onto.save(file=output)

def dynamically_create_instances(iri, output, input_list):
    """create instances from list"""
    onto = get_ontology(iri).load()
    for i in input_list[1:]:
        my_instance = getattr(onto, i[1])(i[0])
        if i[2]:
            my_instance.comment.append(i[2])
    onto.save(file=output)

def json_spec_to_list(dic, triple_list):
    """parse dictionary from json and return list of triples to be inserted"""
# NOTE: relevant relations: requires, is-a, has-part, has-quality,
#  has-value, has-unit
    for key1, val1 in dic.items():
        if isinstance(val1, dict):
            v1 = [k for k, v in val1.items()][0]
            d1 = [v for k, v in val1.items()][0]
            triple_list.append([v1, 'is-a', key1])
            if isinstance(d1, dict):
                for key2, val2 in d1.items():
                    if isinstance(val2, list):
                        for e in val2:
                            triple_list.append([v1, key2, e])
                    if isinstance(val2, dict):
                        v2 = [k for k, v in val2.items()][0]
                    if isinstance(val2, str):
                        v2 = val2
                if key1 == 'specification' and key2 == 'specification':
                    relation = 'has-part'
                elif key1 == 'specification' and not key2 == 'specification':
                    relation = 'has-quality'
                elif key2 == "value":
                    relation = 'has-value'
                elif key2 == 'unit':
                    relation = 'has-unit'
                else:
                    relation = 'has-quality'
                triple_list.append([v1, relation, v2])
                json_spec_to_list(d1, triple_list)
            if isinstance(d1, list):
                for elem in d1:
                    for key2, val2 in elem.items():
                        if isinstance(val2, list):
                            for e in val2:
                                triple_list.append([v1, key2, e])
                        if isinstance(val2, dict):
                            v2 = [k for k, v in val2.items()][0]
                        if isinstance(val2, str):
                            v2 = val2
                    if key1 == 'specification' and key2 == 'specification':
                        relation = 'has-part'
                    elif key1 == 'specification' and not key2 == 'specification':
                        relation = 'has-quality'
                    elif key2 == "value":
                        relation = 'has-value'
                    elif key2 == 'unit':
                        relation = 'has-unit'
                    else:
                        relation = 'has-quality'
                    if isinstance(val2, str):
                        triple_list.append([v1, relation, v2])
                        if relation != 'has-value':
                            triple_list.append([v2, 'is-a', key2])
                    if isinstance(val2, dict):
                        triple_list.append([v1, relation, v2])
                        json_spec_to_list(elem, triple_list)

def create_spec_from_json(iri, output, input_data):
    """create instance for product specification from list"""
    triple_list = []
    json_spec_to_list(input_data, triple_list)
#    [print(i) for i in triple_list]
    onto = get_ontology(iri).load()
    # must create all instances first
    for i in triple_list:
        if i[1] == "is-a":
            my_instance = getattr(onto, i[2])(i[0])
    for i in triple_list:
        if i[1] == "has-quality":
            onto[i[0]].has_quality.append(onto[i[2]])
        if i[1] == "has-part":
            onto[i[0]].has_part.append(onto[i[2]])
        if i[1] == "has-value":
            onto[i[0]].has_value = float(i[2])
        if i[1] == "has-unit":
            onto[i[0]].has_unit = onto[i[2]]
        if i[1] == "requires":
            onto[i[0]].requires.append(onto[i[2]])
        if i[1] == "feature-type":
            onto[i[0]].is_a.append(onto[i[2]])
    onto.save(file=output)

def json_resources_to_list(onto, dic):
    """parse dictionary from json"""
# NOTE: relevant keywords are resource, location, sink, source,
#  process, input, output
# NOTE: cases point/ line/ polygon/ circle hardcoded to fit tbox
    for i in dic:
        my_instance = getattr(onto, dic[i]["parent"])(i)
        if dic[i]["key"] == "resource":
            for k in dic[i]:
                if isinstance(dic[i][k], dict):
                    for sosi in ["source", "sink", "location"]:
                        if dic[i][k]["key"] == sosi:
                            sosi_instance = getattr(onto, dic[i][k]["parent"])(i + '_' +
                                                                               sosi + '_' + k)
                            coord = dic[i][k]["value"]
                            if dic[i][k]["parent"] in ["polygon", "line"]:
                                for c in range(len(coord)):
                                    point = onto.point(i + '_' + sosi + '_' + k + 
                                                       '-point-' + str(c))
                                    point.cartesian_coord_x.append(float(coord[c][0]))
                                    point.cartesian_coord_y.append(float(coord[c][1]))
                                    sosi_instance.specified_by.append(point)
                                    if c != 0:
                                        onto[i + '_' + sosi + '_' + k + '-point-' + str(c)].\
                                            geometrically_neighbors.append(onto\
                                            [i + '_' + sosi + '_' + k + '-point-' + str(c-1)])
                                # rel betw first and last point
                                onto[i + '_' + sosi + '_' + k + '-point-' + str(0)].\
                                    geometrically_neighbors.append(onto\
                                    [i + '_' + sosi + '_' + k + '-point-' + str(len(coord) - 1)])
                            if dic[i][k]["parent"] == "point":
                                sosi_instance.cartesian_coord_x.append(float(coord[0]))
                                sosi_instance.cartesian_coord_y.append(float(coord[1]))
                            if dic[i][k]["parent"] == "circle":
                                for c in coord:
                                    if isinstance(c, list):
                                        point = onto.point(i + '_' + sosi + '_' + k + '_point')
                                        point.cartesian_coord_x.append(float(c[0]))
                                        point.cartesian_coord_y.append(float(c[1]))
                                        sosi_instance.specified_by.append(point)
                                    else:
                                        radius = onto.radius(i + '_' + sosi + '_' + k + '_radius')
                                        radius.has_value = float(c)
                                        sosi_instance.specified_by.append(radius)
                            if sosi == "source":
                                my_instance.can_transport_from.append(sosi_instance)
                            if sosi == "sink":
                                my_instance.can_transport_to.append(sosi_instance)
                            if sosi == "location":
                                my_instance.located_in.append(sosi_instance)
                    # nested elements
                    keywords = {"resource": "has_part",
                                "quality": "has_quality",
                                "process": "can_execute"}
                    if dic[i][k]["key"] in keywords.keys():
                        if dic[i][k]["key"] == "resource":
                            name = k
                        else:
                            name = k + '_' + i
                        my_sub_instance = getattr(onto, dic[i][k]["parent"])(name)
                        getattr(my_instance, keywords[dic[i][k]["key"]]).append(my_sub_instance)
                        json_resources_to_list(onto, {name: dic[i][k]})
        if dic[i]["key"] == "quality":
            # NOTE: there may not be top-level qualities - instance must exist already
            value_kinds = {"value": "has_value",
                           "min-value": "has_min_value",
                           "max-value": "has_max_value"}
            for v in dic[i].keys():
                if v in value_kinds.keys():
                    setattr(onto[i], value_kinds[v], float(dic[i][v]))
                if v == "unit":
                    onto[i].has_unit = onto[dic[i][v]]
                if isinstance(dic[i][v], dict):
                    if dic[i][v]["key"] == "quality":
                        name = v + '_' + i
                        my_sub_instance = getattr(onto, dic[i][v]["parent"])(name)
                        onto[i].has_quality.append(onto[name])
                        json_resources_to_list(onto, {name: dic[i][v]})
        if dic[i]["key"] == "process":
            # only has nested processes, qualities, inputs, outputs, and features
            keywords = {"process": "has_part",
                        "quality": "has_quality",
                        "input": "process_input",
                        "output": "process_output",
                        "feature": "can_realize"}
            for k in dic[i]:
                if isinstance(dic[i][k], dict):
                    if dic[i][k]["key"] in keywords.keys():
                        name = k + '_' + i
                        my_sub_instance = getattr(onto, dic[i][k]["parent"])(name)
                        getattr(onto[i], keywords[dic[i][k]["key"]]).append(onto[name])
                        json_resources_to_list(onto, {name: dic[i][k]})
        if dic[i]["key"] in ["input", "output"]:
        # does not support nested parts w/in the input/ output
            for k in dic[i]:
                if isinstance(dic[i][k], dict):
                    if dic[i][k]["key"] == "quality":
                        name = k + '_' + i
                        my_sub_instance = getattr(onto, dic[i][k]["parent"])(name)
                        onto[i].has_quality.append(onto[name])
                        json_resources_to_list(onto, {name: dic[i][k]})

def create_resource_description_from_json(iri, output, input_data):
    """dynamically create entities from json and add them to onto"""
    onto = get_ontology(iri).load()
    json_resources_to_list(onto, input_data)
    onto.save(file=output)

if __name__ == "__main__":
    print("NOTE: this is not intended as a main module but to provide modules for onto generation")
