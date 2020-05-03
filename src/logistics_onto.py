#!/usr/bin/env python3
"""create logistics onto"""

from owlready2 import DatatypeProperty, FunctionalProperty, get_ontology, Inverse, \
     InverseFunctionalProperty, ObjectProperty, Thing, TransitiveProperty, SymmetricProperty
from onto_gen_modules import get_csv_data, get_json_data, dynamically_create_classes, \
     create_spec_from_json, create_resource_description_from_json

IRI = "http://example.org/logistics-onto.owl"
FILE = "logistics-onto.owl"
CSV_PROCESS_TAXO = "process-taxonomy.csv"
CSV_RESOURCE_TAXO = "resource-taxonomy.csv"
CSV_FEATURE_TAXO = "feature-taxonomy.csv"
JSON_RESOURCE_INSTANCES = "resource-instances.json"
JSON_PRODUCT_SPEC = "product.json"

def build_tbox(iri, output):
    """build tbox and store into output"""
    onto = get_ontology(iri)
    with onto:
        # classes
        class role(Thing):
            comment = ["for defining multiple roles for the same notion, \
                       corresponds to a role in BFO"]
        class process(Thing):
            comment = ["corresponds to a process derived from occurent in BFO"]
        class production_process(process):
            comment = ["a process aiming to create at least one desired output \
                        from at least one input"]
        class logistics_process(production_process): pass
        class manufacturing_process(production_process): pass
        class assembly_process(production_process): pass
        class material_entity(Thing):
            comment = ["notion as used in BFO"]
        class material_object(material_entity):
            comment = ["material entity such as an object according to BFO"]
        class fiat_object_part(material_entity):
            comment = ["notion as used in BFO"]
        class system(role):
            comment = ["a combination of interacting elements organized to \
                        achieve one or more stated purposes [INCOSE SE Handbook], \
                        closest to independent continuant in BFO"]
        class human(material_object):
            comment = ["human being"]
        class specification(Thing):
            comment = ["a specification defines the features a product should have"]
        class product(role):
            comment = ["reification: some system that is the output of a process"]
        class production_resource(role):
            comment = ["some system with capabilities required for creating a product"]
        class logistics_resource(production_resource): pass
        class manufacturing_resource(production_resource): pass
        class assembly_resource(production_resource): pass
        class quality(Thing):
            comment = ["corresponds to a quality in BFO"]
        class physical_feature(role):
            comment = ["feature, in the sense of a physical entity, is an element \
                        related to a physical object, typically the product itself \
                        (Sanfilippo2016)"]
        class information_feature(role):
            comment = ["feature, in the sense of an information entity, is element \
                        of a product model used to reason about the product under \
                        design (Sanfilippo2016)"]
        class form_feature(fiat_object_part):
            comment = ["represents elements via shape properties, e.g., hole or \
                        chamfer [Sanfilippo2016] - these are part of the original object"]
        class functional_feature(quality):
            comment = ["represent functional knowledge, e.g., hole for assembly [Sanfilippo2016]"]
        class material_feature(quality):
            comment = ["represents material properties, e.g., ceramic feature [Sanfilippo2016]"]
        class finishing_feature(quality):
            comment = ["represents features realized during finishing, e.g., cleaned, \
                        degreased or sterilized"]
        class shape(quality):
            comment = ["physical shape of an object"]
        class phase(quality):
            comment = ["chemical phase of a material, i.e., solid, fluid, gas"]
        class viscosity(quality):
            comment = ["property of resistance to flow in any material with fluid \
                        properties [Merriam Webster]"]
        class spatial_region(Thing):
            comment = ["notion as used in BFO"]
        class point(spatial_region):
            comment = ["zero-dimensional spatial region, e.g., expressed using \
                        Cartesian coordinates"]
        class line(spatial_region):
            comment = ["one-dimensional spatial region, defined by two end points"]
        class area(spatial_region):
            comment = ["two-dimensional spatial region, e.g., expressed using \
                        ranges of Cartesian coordinates"]
        class polygon(area):
            comment = ["area in space defined by an arbitrary number of points \
                        connected by edges"]
        class circle(area):
            comment = ["area in space defined by a center and a radius"]
        class orientation(quality):
            comment = ["orientation in space, e.g., expressed using Tait-Bryan angles"]
        class mass(quality):
            comment = ["the property of a body that causes it to have weight in a \
                        gravitational field [WordNet 3.1]"]
        class length(quality):
            comment = ["linear extent in space from one end to the other [WordNet]"]
        class radius(length):
            comment = ["line segment extending from the center of a circle or sphere \
                        to the circumference or bounding surface [Merriam Webster]"]
        class volume(quality):
            comment = ["amount of space occupied by a material entity"]
        class speed(quality):
            comment = ["rate of motion"]
        class throughput(quality):
            comment = ["mass per distance per time"]
        class bounding_box_size(quality):
            comment = ["size of a physical object's bounding box - associated w \
                        three values for each dimension"]
        class moving_restrictions(quality):
            comment = ["any restrictions regarding movements such as fragile, not \
                        to be turned upside down, etc."]
        class unit(Thing):
            comment = ["division of quantity accepted as a standard of measurement \
                        or exchange [WordNet]"]
        # object props
        class has_part(ObjectProperty, TransitiveProperty):
            comment = ["transitive part relationship"]
        class located_in(ObjectProperty):
            comment = ["relation between a material entity and the spatial region \
                        it is located in; also included in BFO"]
        class has_unit(ObjectProperty, FunctionalProperty):
            comment = ["relation to asscoiate a unit with a quality"]
            domain = [unit]
        class prescribes(ObjectProperty, InverseFunctionalProperty):
            comment = ["a specification prescribes a product and its features"]
            domain = [specification]
        class has_quality(ObjectProperty):
            comment = ["describes which qualities an object possesses"]
            range = [quality]
        class specified_by(ObjectProperty):
            comment = ["one thing being specified via another thing, e.g., a line \
                        is defined by its two vertices"]
        class can_transport_from(ObjectProperty):
            domain = [material_object]
        class can_transport_to(ObjectProperty):
            domain = [material_object]
        class connected_to(ObjectProperty, TransitiveProperty):
            comment = ["one production resource is connected to another one, enabling \
                        subsequent process execution"]
            domain = [material_object]
            range = [material_object]
        class specifically_connected_to(connected_to):
            comment = ["relation for feasibility checks specifically for one spec"]
            domain = [material_object]
            range = [material_object]
        class can_execute(ObjectProperty):
            domain = [material_object]
            range = [material_object]
        class executes(ObjectProperty):
            comment = ["can execute on instance level"]
            domain = [material_object]
            range = [material_object]
        class can_realize(ObjectProperty):
            comment = ["relation between a production process and the feature it \
                        realizes; such a feature is either a quality or a \
                        fiat_object_part, e.g., a hole"]
            domain = [production_process]
        class realizes(ObjectProperty):
            comment = ["can realize on instance level"]
            domain = [production_process]
            range = [quality]
        class can_manipulate(ObjectProperty):
            domain = [material_object]
            range = [product]
        class manipulates(ObjectProperty):
            comment = ["can manipulate on instance level"]
            domain = [material_object]
            range = [product]
        class process_input(ObjectProperty):
            comment = ["relation betw a production process and its input"]
            domain = [production_process]
            range = [material_object]
        class process_output(ObjectProperty):
            comment = ["relation betw a production process and its ouput"]
            domain = [production_process]
            range = [material_object]
        class requires(ObjectProperty, TransitiveProperty):
            comment = ["relation betw features, i.e., qualities, indicating that \
                        one must be realized before the other"]
        class immediately_requires(requires, TransitiveProperty):
            comment = ["like requires, but no other feature may be realized betw the two"]
        class can_store(manipulates):
            domain = [logistics_resource]
# TODO: possibly move this to csv so that storage_resource can be set as domain
            range = [material_object]
        class stores(manipulates):
            domain = [logistics_resource]
# TODO: possibly move this to csv so that storage_resource can be set as domain
            range = [material_object]
        class geometrically_neighbors(ObjectProperty, SymmetricProperty):
            comment = ["relation, e.g., between two neighboring vertices of a polygon"]
            domain = [spatial_region]
            range = [spatial_region]
        # datatype props
        class cartesian_coord_x(DatatypeProperty):
            domain = [point]
            range = [float]
        class cartesian_coord_y(DatatypeProperty):
            domain = [point]
            range = [float]
        class cartesian_coord_z(DatatypeProperty):
            domain = [point]
            range = [float]
        class yaw(DatatypeProperty):
            domain = [orientation]
            range = [float]
        class pitch(DatatypeProperty):
            domain = [orientation]
            range = [float]
        class roll(DatatypeProperty):
            domain = [orientation]
            range = [float]
        class has_value(DatatypeProperty, FunctionalProperty): pass
        class has_min_value(has_value): pass
        class has_max_value(has_value): pass
        # axiomatization
        product.is_a.append(Inverse(process_output).some(production_process))
        material_object.is_a.append(has_quality.some(bounding_box_size))
        material_object.is_a.append(has_quality.some(mass))
        material_object.is_a.append(has_quality.exactly(1, point))
        material_object.is_a.append(has_quality.exactly(1, orientation))
        material_object.is_a.append(located_in.some(spatial_region))
        production_process.is_a.append(can_realize.min(1, quality))
        production_resource.is_a.append(can_execute.min(1, production_process))
        logistics_resource.is_a.append(can_execute.min(1, logistics_process))
        manufacturing_resource.is_a.append(can_execute.min(1, manufacturing_process))
        assembly_resource.is_a.append(can_execute.min(1, assembly_process))
        # geometry
        point.is_a.append(cartesian_coord_x.max(1, float))
        point.is_a.append(cartesian_coord_y.max(1, float))
        point.is_a.append(cartesian_coord_z.max(1, float))
        line.is_a.append(specified_by.exactly(2, point))
        circle.is_a.append(specified_by.exactly(1, point))
        circle.is_a.append(specified_by.exactly(1, radius))
        polygon.is_a.append(specified_by.min(3, point))
        orientation.is_a.append(yaw.max(1, float))
        orientation.is_a.append(pitch.max(1, float))
        orientation.is_a.append(roll.max(1, float))
        # qualities
        bounding_box_size.is_a.append(has_quality.exactly(3, length))
        specification.is_a.append(prescribes.min(1, product))
        mass.is_a.append(has_value.exactly(1, float))
        mass.is_a.append(has_unit.exactly(1, unit))
        length.is_a.append(has_value.exactly(1, float))
        length.is_a.append(has_unit.exactly(1, unit))
        volume.is_a.append(has_value.exactly(1, float))
        volume.is_a.append(has_unit.exactly(1, unit))

    # instances
    kg = unit("kg")
    m = unit("m")
    m_p_s = unit("m_p_s")
    kg_p_m_p_s = unit("kg_p_m_p_s")
    ccm = unit("ccm")
    ccm_p_s = unit("ccm_p_s")
    solid = phase("solid")
    fluis = phase("fluid")
    gas = phase("gas")

    onto.save(file=output)

def main():
    """create main classes and load taxonomies"""
    build_tbox(IRI, FILE)
    dynamically_create_classes(IRI, FILE, get_csv_data(CSV_PROCESS_TAXO))
    dynamically_create_classes(IRI, FILE, get_csv_data(CSV_RESOURCE_TAXO))
    dynamically_create_classes(IRI, FILE, get_csv_data(CSV_FEATURE_TAXO))
    create_spec_from_json(IRI, FILE, get_json_data(JSON_PRODUCT_SPEC))
    create_resource_description_from_json(IRI, FILE, get_json_data(JSON_RESOURCE_INSTANCES))
#    json_resources_to_list(get_json_data(JSON_RESOURCE_INSTANCES))

if __name__ == "__main__":
    main()
