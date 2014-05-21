import json
import os
import unittest
from jinja2 import TemplateNotFound
from cftpl.template import DEFAULT_TEMPLATES, CFTemplate
from cftpl.config import get_settings


class GenericManagerTestCase(unittest.TestCase):
    def test_default_templates(self):
        self.assertTrue(os.path.isfile(os.path.join(DEFAULT_TEMPLATES, 'default.yaml')))


class CoudFormationConfigurationTestCase(unittest.TestCase):
    def setUp(self):
        self.example_config = get_settings('testdata/config.py')
        self.test_result_json = open(os.path.join(self.example_config['TEMPLATE_PATH'], 'output.json')).read()
        self.test_result = json.loads(self.test_result_json)

    def test_init_settings(self):
        testpath = '/tmp'
        self.example_config['TEMPLATE_PATH'] = testpath
        self.example_config['FILES'] = {}
        conf = CFTemplate(self.example_config)
        self.assertEqual(conf.config['TEMPLATE_PATH'], testpath)

    def test_create_fails(self):
        self.example_config['TEMPLATE_PATH'] = '/tmp'
        self.example_config['FILES'] = {}
        conf = CFTemplate(self.example_config)
        self.assertRaises(TemplateNotFound, conf.create)

    def test_create_yaml(self):
        self.example_config['TEMPLATE'] = 'prod.yaml'
        conf = CFTemplate(self.example_config)
        created = json.loads(conf.create_json())
        self.assertEqual(created, self.test_result)

    def test_create_json(self):
        conf = CFTemplate(self.example_config)
        created = json.loads(conf.create_json())
        self.assertEqual(created, self.test_result)