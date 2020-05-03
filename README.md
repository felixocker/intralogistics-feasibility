# intralogistics-feasibility
ontology-based feasibility checker for intralogistics


# Contents
## src - knowledge graph creation and adaption
* logistics_onto.py - tbox and dynamic abox creation
* onto_gen_modules.py - modules for dynamic ontology population
* executequery.py - module for executing SPARQL query, returns nested list of results
* reachability.py - generic reachability inference using geometric descriptions
* specific_reachability.py - product specific feasibility check, takes qualities into account

## data - input files for knowledge graph creation
* resource-taxonomy.csv - taxonomy of typical logistics resources, according to w Jünemann 1989
* process-taxonomy.csv - incomplete collection of several typical production resources
* feature-taxonomy.csv - collection of several classes of feature relevant for the minimal example
* resources.json - input data for the minimal exampe's resources on abox level
* product.json - input data for the minimal example's specification 

## queries
* prefixes.sparql - reusable set of prefixes
* find_transport_resources.sparql - query that returns all transport resources
* find_non_transport_resources.sparql - query that returns all resources that are not transport resources
* find_viable_transport_resources.sparql - returns transport resources that can transport the product in question
* feature_feasibility.sparql - returns infeasible features

# Copyright
Copyright © 2019 Technical University of Munich - Institute of Automation and Information Systems. <https://www.mw.tum.de/en/ais/homepage/>

All rights reserved. Contact: [felix.ocker@tum.de](mailto:felix.ocker@tum.de)
