__author__ = 'ash'

import yaml
import string

class YamlDoc:

    nodes = []

    def __init__(self)


    def load_from_yaml(self,docName):
        with open(docName,'r') as f:
            self = yaml.load(f)

    def