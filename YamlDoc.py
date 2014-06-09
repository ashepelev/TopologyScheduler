__author__ = 'ash'

import yaml
import string

class YamlDoc:

    nodes = []

    def load_from_yaml(self,docName):
        with open(docName,'r') as f:
            self.nodes = yaml.load(f)
