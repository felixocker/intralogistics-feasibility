# intralogistics-feasibility
ontology-based feasibility checker for intralogistics\
implementation for the paper "Towards Providing Feasibility Feedback in Intralogistics Using a Knowledge Graph" presented at IEEE INDIN20

# Contents
## src - knowledge graph creation and adaption
* main.py - convenience module for running the following scripts
* logistics_onto.py - tbox and dynamic abox creation
* onto_gen_modules.py - modules for dynamic ontology population
* executequery.py - module for executing SPARQL query, returns nested list of results
* reachability.py - generic reachability inference using geometric descriptions
* specific_reachability.py - product specific feasibility check, takes qualities into account

## data - input files for knowledge graph creation
* resource-taxonomy.csv - taxonomy of typical logistics resources, according to Jünemann 1989
* process-taxonomy.csv - incomplete collection of several typical production resources
* feature-taxonomy.csv - collection of several classes of features relevant for the minimal example
* resources.json - input data for the minimal example's resources on abox level
* product.json - input data for the minimal example's specification 

## queries
* prefixes.sparql - reusable set of prefixes
* find_transport_resources.sparql - query that returns all transport resources
* find_non_transport_resources.sparql - query that returns all resources that are not transport resources
* find_viable_transport_resources.sparql - returns transport resources that can transport the product in question
* feature_feasibility.sparql - returns infeasible features

# Citation
Please use the following bibtex entry:
```
@inproceedings{ocker2020indin,
author = {Ocker, Felix and Vogel-Heuser, Birgit and Fischer, Juliane},
booktitle = {INDIN},
pages = {380--387},
publisher = {IEEE},
title = {{Towards Providing Feasibility Feedback in Intralogistics Using a Knowledge Graph}},
year = {2020}
}
```

# License
GPL v3.0

# Contact
Felix Ocker - [felix.ocker@tum.de](mailto:felix.ocker@tum.de)\
Technical University of Munich - Institute of Automation and Information Systems <https://www.mw.tum.de/en/ais/homepage/>
