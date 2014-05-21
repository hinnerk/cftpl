from __future__ import print_function
import base64
import json
import os.path
import re
import logging
from jinja2 import FileSystemLoader, Environment, ChoiceLoader, PrefixLoader
import yaml
import copy


logger = logging.getLogger(__name__)

DEFAULT_TEMPLATES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')


def base64_converter(data):
    """
    Converts strings to base64. Available in Jinja2 as an additional filter.
    """
    data = re.sub(r'^#+\s+.*', '', data, flags=re.MULTILINE)  # remove comments
    data = re.sub(r'^\n\n', "", data, flags=re.MULTILINE)  # remove empty lines
    return base64.b64encode(data)


class CFTemplate(object):
    def __init__(self, configuration=None):
        # we're going to modify the config so better use our own copy.
        self.config = {} if not configuration else copy.deepcopy(configuration)
        for name, filename in self.config['FILES'].iteritems():
            path = os.path.join(self.config['TEMPLATE_PATH'], filename)
            self.config['FILES'][name] = open(path).read()
        simple_loader = FileSystemLoader(DEFAULT_TEMPLATES)
        self.env = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            loader=ChoiceLoader([
                FileSystemLoader(self.config['TEMPLATE_PATH']),
                simple_loader,  # implicit inheritance
                PrefixLoader({'!simple': simple_loader})  # explicit one
            ]),
            extensions=self.config['JINJA_EXTENSIONS'],
        )
        self.env.filters.update({'base64': base64_converter})
        self.env.filters.update(self.config['JINJA_FILTERS'])

    def create(self):
        template = self.env.get_template(self.config['TEMPLATE'])
        return template.render(self.config)

    def create_json(self):
        data = self.create()    # attach you breakpoint to the next line to peek at the yaml code ;)
        if self.config['TEMPLATE'].lower().endswith('yaml'):
            return json.dumps(yaml.load(data), indent=self.config['JSON_INDENT'])
        # load/dump cycle to make sure the given json is valid (and to allow formatting)
        return json.dumps(json.loads(data), indent=self.config['JSON_INDENT'])


