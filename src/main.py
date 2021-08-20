#!/usr/bin/env python3
"""create intralogistics onto, infer reachability, and check feasibility"""

import os

def example():
    # iri = "http://example.org/logistics-onto.owl"
    # ontofile = "logistics-onto.owl"
    os.system("python logistics_onto.py")
    os.system("python reachability.py")
    os.system("python specific_reachability.py")

if __name__ == '__main__':
    example()
